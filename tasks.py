'''
Class definition of components
'''
from config import *

class res:
    def __init__(self, idx, length):
        self.idx = idx
        self.holder = None
        self.waiter = []
        self.length = length
    def __str__(self):
        return "res#{}".format(self.idx)

class snippet:
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
    def acquire(self):  
        if self.locksafe():
            if self.res != None:
                self.res.holder = self.belong_to
    def tick(self):
        if self.locksafe():
            self.progress += 1
            return True
        return False
    def release_and_progress(self):
        self.belong_to.cur_snippet = self.next
        if self.type == STYPE_CRITICAL:
            self.res.holder = None

    # properties
    def locksafe(self):
        return self.res == None or self.res.holder == None or self.res.holder == self.belong_to
    def done(self):
        return self.progress >= self.length
    def preemptable(self):
        return self.type != STYPE_SWITCH

class task:
    def __init__(self, idx, used_res, sections, period, deadline):
        self.idx = idx
        self.priority = 0
        self.used_res = used_res
        self.section_tuples = sections   # list of (res, length)
        self.period = period
        self.deadline = deadline
        self.target_core = None
    def __str__(self):
        section_print = ""
        for section in self.section_tuples:
            section_print += " ({}:{})".format(section[0].__str__(), section[1])
        return "task#{}pri#{}:{}".format(self.idx, self.priority, section_print)

    def new_instance(self, cur_time):
        snippets = []
        for (res, length) in self.section_tuples:
            snippets.append(snippet(res, length))
        # link between snippets to enable next
        for i in range(0, len(snippets) - 1):
            snippets[i].next = snippets[i+1]
        new_inst = instance(self.idx, self.priority, snippets, cur_time, cur_time + self.deadline, self.target_core)
        for s in new_inst.snippets:
            s.belong_to = new_inst
        return new_inst

class instance:
    def __init__(self, idx, priority, snippets, arrival, ddl, core):
        # tags
        self.idx = idx
        self.target_core = core
        self.base_pri = priority
        # runtime states
        self.snippets = snippets
        self.cur_snippet = snippets[0]
        self.virgin = True
        # time records
        self.arrival = arrival
        self.activation = -1
        self.completion = -1
        self.ddl = ddl
    
    @property
    def runtime_pri(self):
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
