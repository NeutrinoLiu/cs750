'''
Implementation of a single core that work as a local PCP
'''

# core states
from config import *
from tasks import Snippet

class Core:
    MrsP_ctr = 0

    def __init__(self, idx):
        self.idx = idx
        self.affi_tasks = []
        self.ceiling_table = {}         # res idx -> max priority
        # runtime state
        self.pool = []                  # instance pool
        self.accomplished = []          # accomplished instances
        self.running_snippet = None     # current running SNIPPET
        self.time = 0
        self.history = []               # running history

    def __str__(self):
        return "core#{}\tuti{:.3f}:\t{}".format(self.idx, self.utilization, list(map(lambda x: "t{}".format(x.idx), self.affi_tasks)))


    def trace(self, max_time=0):
        if max_time == 0:
           return "{}".format("\t".join(self.history))
        return "{}".format("\t".join(self.history[:max_time]))
    
    def avg_resp_time(self):
        total = 0
        for done_inst in self.accomplished:
            total += done_inst.completion - done_inst.activation
        if len(self.accomplished) == 0:
            return 0, 0
        return len(self.accomplished), total / len(self.accomplished)
    
    @property
    def utilization(self):
        uti = 0
        for at in self.affi_tasks:
            uti += at.utilization
        return uti

    def enroll(self, inst):
        inst.cur_host = self
        self.pool.append(inst)

    # check condition and acquire lock
    def uptick(self):

        # a) if there was no snippet running, or last instance has finished
        if self.running_snippet == None:
            # directly find the top pri inst and run it
            top_pri_inst = self.__highest_pri_inst()
            if top_pri_inst == None:
                return
            if top_pri_inst.virgin:
                top_pri_inst.virgin = False
                top_pri_inst.activation = self.time
            self.running_snippet = top_pri_inst.cur_snippet
            self.running_snippet.pre_tick()  # its fine to double acquire if you are the holder
            return 

        # b) if it is non-preemptable snippet and not done, i.e. switch
        if not self.running_snippet.preemptable() and not self.running_snippet.done():
            # keep run it
            return

        # c) if there is a preemptable inst running in the last tick
        #    or a finished switch snippet in the last tick
        previous_inst = self.running_snippet.belong_to
        top_pri_inst = self.__highest_pri_inst(self.running_snippet.belong_to)
        if top_pri_inst == None:        # no avail inst can run
            self.running_snippet = None
            return
        if top_pri_inst.virgin:
            top_pri_inst.virgin = False
            top_pri_inst.activation = self.time
        
        # c-1) if top-pri inst is different from previous one
        # preemtion happens!!
        if top_pri_inst != previous_inst:
            # try to migrate the old inst to where his holding is welcome
            if ENABLE_MRSP:
                if self.running_snippet.type == STYPE_CRITICAL and self.running_snippet.lockholding():
                    held_res = self.running_snippet.res
                    waiter = held_res.spoony()
                    # print("MrsP might be triggered! {} is spin for r{}".format(waiter, held_res))
                    if waiter and self != waiter.cur_host:
                        Core.migrate(previous_inst, self, waiter.cur_host)

            # insert a switch snippet for the new inst
            switch_snippet = Snippet(None, SWITCH_COST, context_switch=1)
            switch_snippet.belong_to = top_pri_inst
            switch_snippet.next = top_pri_inst.cur_snippet # fantastic design 
            self.running_snippet = switch_snippet
            # no need to pretick for switch snippet
            return

        # c-2) we will continue the same inst in the last tick
        self.running_snippet = top_pri_inst.cur_snippet 
        self.running_snippet.pre_tick()  # its fine to double acquire if you are the holder
        return 
    
    # make progress
    def intertick(self):
        if self.running_snippet != None:
            cur_inst = self.running_snippet.belong_to
            if self.running_snippet.tick():     # snippet progress +1
                if self.running_snippet.type == STYPE_NON_CRIT:
                    self.history.append("t{}#{}_p{}_NC".format(cur_inst.idx, cur_inst.order, cur_inst.runtime_pri))
                if self.running_snippet.type == STYPE_CRITICAL:
                    self.history.append("t{}#{}_p{}_CR".format(cur_inst.idx, cur_inst.order, cur_inst.runtime_pri))
                if self.running_snippet.type == STYPE_SWITCH:
                    self.history.append("t{}#{}_CSWIT".format(cur_inst.idx, cur_inst.order))
            else:
                self.history.append("t{}#{}_p{}_SP".format(cur_inst.idx, cur_inst.order, cur_inst.runtime_pri))
        else:
            self.history.append("__IDLING__")

    # release lock and conclude progress
    def downtick(self):
        self.time += 1
        if self.running_snippet == None:
            return
        cur_inst = self.running_snippet.belong_to
        if self.running_snippet.done():
            self.running_snippet.post_tick()
            # VIP
            cur_inst.cur_snippet = self.running_snippet.next # make progress
            if cur_inst.done():
                self.__retire(cur_inst)         # one may retire in the foreign core if the last is a migrated critical snippet
                return
            # if the cur inst does not belong to this core, go home
            # careful! switch snippet should be ignored    
            if not cur_inst.at_home(self) and not self.running_snippet.type == STYPE_SWITCH:
                Core.go_home(cur_inst, from_core=self)
            return
        if cur_inst.ddl <= self.time:
            self.running_snippet.post_tick()
            self.resign(cur_inst)
            print("t{}#{} Deadline Missed !".format(cur_inst.idx, cur_inst.order))
            raise Exception("Deadline Missed !")

    def __retire(self, inst):
        inst.completion = self.time
        inst.cur_host = None
        self.accomplished.append(inst)
        self.pool.remove(inst)

    def resign(self, inst):
        inst.cur_host = None
        try:
            self.pool.remove(inst)
        except ValueError:
            print("ERROR: {} not found in core#{}".format(inst, self.idx)) 


    def __highest_pri_inst(self, previous = None):
        highest = previous
        if highest not in self.pool:
            highest = None
        for inst in self.pool:
            if highest == None:
                highest = inst
            elif inst.runtime_pri > highest.runtime_pri:
                highest = inst
        if highest == None or highest.done():
            return None
        return highest

    # task migration related!
    @classmethod
    def migrate(cls, inst, from_core, to_core):
        # print("MrsP is triggered! move {} from core#{} to core#{}".format(inst, from_core.idx, to_core.idx))
        cls.MrsP_ctr += 1
        from_core.resign(inst)
        inst.mig_pri = to_core.running_snippet.belong_to.runtime_pri + 1
        to_core.enroll(inst)

    @classmethod
    def go_home(cls, inst, from_core):
        # print("MrsP done! move {} from core#{} back to core#{}".format(inst, from_core.idx, inst.target_core.idx))
        from_core.resign(inst)
        inst.mig_pri = -1
        inst.target_core.enroll(inst)


# simulator modules 
class Task_launcher:
    def __init__(self, tasks):
        self.tasks = tasks
        self.cur_time = 0
    def tick(self):
        output_insts = []       # output instances
        for task in self.tasks:
            if self.cur_time % task.period == task.initial:
                output_insts.append(task.new_instance(self.cur_time))
        self.cur_time += 1
        return output_insts

