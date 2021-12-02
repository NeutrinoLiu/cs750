'''
Implementation of a single core that work as a local PCP
'''

# core states
from config import *
from tasks import snippet

class core:
    def __init__(self, idx):
        self.idx = idx
        self.affi_tasks = []
        self.ceiling_table = {}         # res idx -> max priority
        # runtime state
        self.pool = []
        self.accomplished = []
        self.running_snippet = None             # current running SNIPPET
        self.time = 0
        self.history = []
    def to_string(self, max_time=0):
        if max_time == 0:
            "core#{}: {}".format(self.idx, " ".join(self.history))
        return "core#{}: {}".format(self.idx, " ".join(self.history[:max_time]))

    def enroll(self, inst):
        self.pool.append(inst)

    # check condition and acquire lock
    def uptick(self):
        # if there was no snippet running 
        if self.running_snippet == None:
            top_pri_inst = self.__highest_pri_inst()
            if top_pri_inst == None:
                return
            if top_pri_inst.virgin:
                top_pri_inst.virgin = False
                top_pri_inst.activation = self.time
            self.running_snippet = top_pri_inst.cur_snippet
            self.running_snippet.acquire()  # its fine to double acquire if you are the holder
            return 
        # non-preemptable snippet and not done, i.e. switch, keep running
        if not self.running_snippet.preemptable() and not self.running_snippet.done():
            return
        # if there is a preemptable snippet running in last tick and not finished
        # or a finished switch
        previous_inst = self.running_snippet.belong_to
        top_pri_inst = self.__highest_pri_inst(self.running_snippet.belong_to)
        if top_pri_inst == None:    # no other inst can run
            self.running_snippet = None
            return
        if top_pri_inst.virgin:
            top_pri_inst.virgin = False
            top_pri_inst.activation = self.time
        if top_pri_inst != previous_inst:       # if next inst is different from previous one
            switch_snippet = snippet(None, SWITCH_COST, context_switch=1)
            switch_snippet.belong_to = top_pri_inst
            switch_snippet.next = top_pri_inst.cur_snippet
            self.running_snippet = switch_snippet
            return
        self.running_snippet = top_pri_inst.cur_snippet
        self.running_snippet.acquire()  # its fine to double acquire if you are the holder
        return 
    
    # make progress
    def intertick(self):
        if self.running_snippet != None:
            cur_inst = self.running_snippet.belong_to
            if self.running_snippet.tick():     # snippet progress +1
                if self.running_snippet.type == STYPE_NON_CRIT:
                    self.history.append("t{}_p{}_NC".format(cur_inst.idx, cur_inst.runtime_pri))
                if self.running_snippet.type == STYPE_CRITICAL:
                    self.history.append("t{}_p{}_CR".format(cur_inst.idx, cur_inst.runtime_pri))
                if self.running_snippet.type == STYPE_SWITCH:
                    self.history.append("t{}_CSWIT".format(cur_inst.idx))
            else:
                self.history.append("t{}_SPINN".format(cur_inst.idx))
        else:
            self.history.append("_IDLING_")

    # release lock and conclude progress
    def downtick(self):
        self.time += 1
        if self.running_snippet == None:
            return
        if self.running_snippet.done():
            self.running_snippet.release_and_progress()
            cur_inst = self.running_snippet.belong_to
            if cur_inst.done():
                self.__retire(cur_inst)

    def __retire(self, inst):
        inst.completion = self.time
        self.accomplished.append(inst)
        self.pool.remove(inst)

    def __highest_pri_inst(self, previous = None):
        highest = previous
        for inst in self.pool:
            if highest == None:
                highest = inst
            elif inst.runtime_pri > highest.runtime_pri:
                highest = inst
        if highest == None or highest.done():
            return None
        return highest

# simulator modules 
class task_launcher:
    def __init__(self, tasks):
        self.tasks = tasks
        self.cur_time = 0
    def tick(self):
        output_insts = []       # output instances
        for task in self.tasks:
            if self.cur_time % task.period == 0:
                output_insts.append(task.new_instance(self.cur_time))
        self.cur_time += 1
        return output_insts

