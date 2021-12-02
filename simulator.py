import random
import math
import time
from config import *
from tasks import *
from processor import *
from functools import reduce
from utils import *

'''
Simulation paras
Simulation input generators
Simulation pipeline
'''

# GENERATOR Implementations ================================================
def gen_simple():
    r0 = Res(0, 5)
    r1 = Res(1, 5)
    r2 = Res(2, 5)
    r3 = Res(3, 5)
    t0 = Task(
        0,
        [r0],
        [(None,1), (r0,5), (None,1)],
        40,
        40
    )
    t1 = Task(
        1,
        [r1, r2],
        [(None,1), (r1,5), (None,1), (r2,5), (None,1)],
        60,
        60
    )
    t2 = Task(
        2,
        [r1, r3],
        [(None,4), (r1,5), (None,1), (r3,5), (None,1)],
        80,
        80
    )
    t3 = Task(
        3,
        [r3],
        [(None,1), (r3,5), (None,1)],
        30,
        30
    )
    return list([r0, r1, r2, r3]), list([t0, t1, t2, t3])

# NOTICE: this is where we should change for different algos
def gen_res(num, min_len, max_len):
    res_set = []
    for index in range(0, num):
        res_set.append(Res(index, random.randint(min_len, max_len)))
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
        non_crit_sublens = int_ripper(non_crit_len, num_used_res + 1)
        for i in range(0, num_used_res):
            section_len = non_crit_sublens[i]
            if section_len > 0:
                sections.append( (None, section_len) )
            sections.append( (used_res[i], used_res[i].length) )
        if non_crit_sublens[-1] > 0:
            sections.append( (None, non_crit_sublens[-1]) )
        # generate total period
        period = gen_period(critical_len + non_crit_len, UTILIZATION)
        new_task = Task(index, used_res, sections, period, period)
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
        core_set.append(Core(index))
    return core_set

def gen_task2core_map_safe(tasks, cores): # task_id -> core_obj
    # a random mapper 
    for t in tasks:
        target_core = random.choice(cores)
        while target_core.utilization + t.utilization > 1:
            target_core = random.choice(cores)
        target_core.affi_tasks.append(t)
        t.target_core = target_core
    for c in cores:
        task_list = ""
        for t in c.affi_tasks:
            task_list += "\ttask#{}".format(t.idx)
        print("core#{}/uti{:.3f}:{}".format(c.idx, c.utilization, task_list))
        
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
if SIMPLE_TASKS:
    res_set, task_set = gen_simple()
else:
    res_set = gen_res(N_RES, MIN_LEN, MAX_LEN)
    task_set = gen_tasks(N_TASK, res_set, ALPHA)
# generate priority according to the period
gen_priority(task_set)
print("\n[ TASK STRUCTURE ]")
for t in task_set:
    print(t)

# RTS MODULES
# generate cores
core_set = gen_cores(N_CORE)
# maps between task and core
print("\n[ TASK-CORE MAP ]")
gen_task2core_map_safe(task_set, core_set)
# generate local ceiling table for each core
for c in core_set:
    gen_ceiling_table(c, res_set)
# instance launcher
launcher = Task_launcher(task_set)

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

print("\n[ SIMULATION RESULT ]")
for i in range(0, N_CORE):
    print(core_set[i].trace(480))

print("\ntotal simulation time {}, for {} ticks".format(time.time() - start_time, T_MAX))