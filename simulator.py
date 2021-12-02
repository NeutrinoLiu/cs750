import random
import math
import time
from config import *
from tasks import *
from processor import *
from functools import reduce

'''
Simulation paras
Simulation input generators
Simulation pipeline
'''

# GENERATOR Implementations ================================================
# NOTICE: this is where we should change for different algos
def gen_res(num, min_len, max_len):
    res_set = []
    for index in range(0, num):
        res_set.append(res(index, random.randint(min_len, max_len)))
    return res_set

def gen_tasks(num, res_set, alpha):
    task_set = []
    for index in range(0, num):

        # the res this task may use
        num_used_res = random.randint(1, len(res_set))
        used_res = random.sample(res_set, num_used_res)
        # the length of critical and non-crit sections
        critical_len = 0
        for r in used_res:
            critical_len += r.length
        non_crit_len = critical_len * alpha
        # generate section list
        sections = []
        for i in range(0, num_used_res):
            sub_crit_len = random.randint(0, non_crit_len)
            if sub_crit_len > 0:
                sections.append( (None, sub_crit_len) )
                non_crit_len -= sub_crit_len
            sections.append( (used_res[i], used_res[i].length) )
        if non_crit_len > 0:
            sections.append( (None, non_crit_len) )
        # generate total period
        period = gen_period(critical_len + non_crit_len, UTILIZATION)
        new_task = task(index, used_res, sections, period, period)
        task_set.append(new_task)  # set ddl the same as period
    return task_set

def gen_period(computation_time, utilization):
    min_period = math.ceil(computation_time/utilization)
    # fixed utilization 
    # return min_period
    # random utilization
    return random.randint(min_period, min_period * 2)

def gen_cores(num):
    core_set = []
    for index in range(0, num):
        core_set.append(core(index))
    return core_set

def gen_task2core_map_random(tasks, cores): # task_id -> core_obj
    # a random mapper 
    for t in tasks:
        target_core = random.choice(cores)
        target_core.affi_tasks.append(t)
        t.target_core = target_core
        
def gen_priority(task_set):
    task_set.sort(key = lambda x: x.period)
    max_priority = len(task_set)
    for i in range(0, max_priority):
        task_set[i].priority = max_priority - i

def gen_ceiling_table(c, res_set):
    table = {}
    for r in res_set:
        pri = 0
        for t in c.affi_tasks:
            if r in t.used_res:
                pri = max(pri, t.priority)
        table[r.idx] = pri
    c.ceiling_table = table

def inst_migration(core_from, core_to, inst):
    pass

# INIT ===================================================================

# COMPONENTS
# generate resources and tasks
res_set = gen_res(N_RES, MIN_LEN, MAX_LEN)
task_set = gen_tasks(N_TASK, res_set, ALPHA)
# generate priority according to the period
gen_priority(task_set)
for t in task_set:
    print(t)

# RTS MODULES
# generate cores
core_set = gen_cores(N_CORE)
# maps between task and core
gen_task2core_map_random(task_set, core_set)
# generate local ceiling table for each core
for c in core_set:
    gen_ceiling_table(c, res_set)
# instance launcher
launcher = task_launcher(task_set)

# PIPELINE ===============================================================
t = 0
start_time = time.time()
while t < T_MAX:
    new_insts = launcher.tick()

    # put the new insts into the pool of its corresponded core
    for inst in new_insts:
        inst.target_core.enroll(inst)
    
    # each core do sth
    for c in core_set:
        c.uptick()
    for c in core_set:
        c.intertick()
    for c in core_set:
        c.downtick()
    
    t += 1

for i in range(0, N_CORE):
    print(core_set[i].to_string(100))

print("total simulation time {}, for {} ticks".format(time.time() - start_time, T_MAX))