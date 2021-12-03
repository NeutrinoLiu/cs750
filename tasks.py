'''
Class definition of components
'''
from config import *

class Res:
    def __init__(self, idx, length):
        self.idx = idx
        self.length = length
        # runtime states
        self.__holder = None          # which instance is the holder
        self.__wait_list = []
    def __str__(self):
        return "r{}".format(self.idx)

    # wait list related
    def subscribe(self, inst):
        if inst not in self.__wait_list:
            self.__wait_list.append(inst)
    def unsubscribe(self, inst):
        if inst in self.__wait_list:
            self.__wait_list.remove(inst)
    def spoony(self):           # those who want it but do not have it.
        if len(self.__wait_list) > 0:
            return self.__wait_list[0]
        return None
    
    # holder related
    def acquire(self, inst):
        if self.__holder == inst:
            self.unsubscribe(inst)
            return True
        elif self.__holder == None and (self.spoony() == None or self.spoony() == inst):
            self.unsubscribe(inst)
            self.__holder = inst
            return True
        else:
            self.subscribe(inst)
            return False
    def release(self):
        self.__holder = None
    def held_by(self, inst):
        return self.__holder == inst

class Snippet:
    def __init__(self, res, length, context_switch = 0):
        self.progress = 0
        self.belong_to = None
        self.next = None
        if context_switch == 1:
            self.type = STYPE_SWITCH
            self.res = None
            self.length = SWITCH_COST
        elif res:
            self.type = STYPE_CRITICAL
            self.res = res
            self.length = length
        else:
            self.type = STYPE_NON_CRIT
            self.res = None
            self.length = length

    # tick behaviors
    def pre_tick(self):  
        if self.res != None:
            return self.res.acquire(self.belong_to)
        return True
    def tick(self):
        if self.lockholding():
            self.progress += 1
            return True
        return False
    def post_tick(self):
        if self.type == STYPE_CRITICAL:
            self.res.release()

    # properties
    def lockholding(self):
        return self.res == None or self.res.held_by(self.belong_to)
    def done(self):
        return self.progress >= self.length
    def preemptable(self):
        return self.type != STYPE_SWITCH

class Task:
    def __init__(self, idx, used_res, sections, period, deadline, initial = 0):
        self.idx = idx
        self.priority = 0
        self.used_res = used_res
        self.section_tuples = sections   # list of (res, length)
        self.period = period
        self.deadline = deadline
        self.initial = initial
        self.target_core = None
    
    def __str__(self):
        section_print = ""
        for section in self.section_tuples:
            section_print += "\t{}:{}".format(section[0].__str__() if section[0] else "nc", section[1])
        return "task#{}/pri#{}/T{}/uti{:.3f}:{}".format(self.idx, self.priority, self.period, self.utilization, section_print)

    @property
    def utilization(self):
        length = 0
        for st in self.section_tuples:
            length += st[1]
        return length/self.period
    def new_instance(self, cur_time):
        snippets = []
        for (res, length) in self.section_tuples:
            snippets.append(Snippet(res, length))
        # link between snippets to enable next
        for i in range(0, len(snippets) - 1):
            snippets[i].next = snippets[i+1]
        new_inst = Instance(self.idx, int((cur_time-self.initial)/self.period), self.priority, snippets, cur_time, cur_time + self.deadline, self.target_core)
        for s in new_inst.snippets:
            s.belong_to = new_inst
        return new_inst

class Instance:
    def __init__(self, idx, order, priority, snippets, arrival, ddl, core):
        # tags
        self.idx = idx
        self.order = order
        self.target_core = core
        self.base_pri = priority
        # runtime states
        self.cur_host = None
        self.snippets = snippets
        self.cur_snippet = snippets[0]
        self.virgin = True
        self.mig_pri = -1
        # time records
        self.arrival = arrival
        self.activation = -1
        self.completion = -1
        self.ddl = ddl
    def __str__(self):
        return "t{}#{}_core#{}".format(self.idx, self.order, self.cur_host.idx if self.cur_host else "None")
    
    @property
    def runtime_pri(self):
        if self.mig_pri > 0:    # if it is in the state of migration
            return self.mig_pri
        cur_snippet = self.cur_snippet
        if cur_snippet == None:
            return 0
        if cur_snippet.type == STYPE_NON_CRIT:
            return self.base_pri
        if cur_snippet.type == STYPE_SWITCH:
            return MAX_PRI
        if cur_snippet.type == STYPE_CRITICAL:
            host = self.target_core
            return host.ceiling_table[cur_snippet.res.idx]

    def done(self):
        return self.cur_snippet == None
    def at_home(self, cur_core):
        return self.target_core == cur_core
