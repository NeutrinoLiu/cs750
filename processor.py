'''
Implementation of a single core that work as a local PCP
'''

# core states
from tasks import NON_CRIT, CRITICAL


IDLE = 0
RUNNING = 1
SPINNING = 2
SWITCH = 3

class core:
    def __init__(self, idx):
        self.idx = idx
        self.pool = []
        self.accomplished = []
        self.affi_tasks = []
        self.running = None             # current running SNIPPET
        self.ceiling_table = {}         # res idx -> max priority
        self.time = 0
    def enroll(self, inst):
        self.pool.append(inst)

    # check condition and acquire lock
    def uptick(self):
        # if there is no snippet running / accomplished in last tick
        if self.running == None:
            top_pri_inst = self.__highest_pri_inst()
            if top_pri_inst.virgin:
                top_pri_inst.virgin = False
                top_pri_inst.activation = self.time
            self.running = top_pri_inst.cur_snippet
            self.running.acquire()  # its fine to double acquire if you are the holder
            return
        # if there is a snippet running in last tick and not finished
        if self.running.preemptable():
            top_pri_inst = self.__highest_pri_inst(self.running.belong_to)
            if top_pri_inst.virgin:
                top_pri_inst.virgin = False
                top_pri_inst.activation = self.time
            self.running = top_pri_inst.cur_snippet
            self.running.acquire()  # its fine to double acquire if you are the holder
            return 
        # non-preemptable snippet, keep running
        self.running.acquire()      # its fine to double acquire if you are the holder
    
    # make progress
    def intertick(self):
        if self.running != None:
            self.running.tick()
    
    # release lock and conclude progress
    def downtick(self):
        self.time += 1
        if self.running == None:
            return
        if self.running.done():
            self.running.release_and_progress()
            cur_inst = self.running.belong_to
            if cur_inst.cur_snippet == None:
                self.__retire(cur_inst)
            self.running = None

    def __retire(self, inst):
        inst.completion = self.time
        self.accomplished.append(inst)
        self.pool.remove(inst)

    def __highest_pri_inst(self, previous = None):
        highest = previous
        for inst in self.pool:
            if highest == None:
                highest = inst
            else:
                if inst.runtime_pri > highest.runtime_pri:
                    highest = inst
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

