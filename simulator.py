import random
import math
import time
from config import *
from simple_tasks import gen_simple
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
        # num_used_res = random.randint(1, len(res_set) * 2)
        num_used_res = len(res_set) * 2
        used_res = []
        for i in range(0, num_used_res):
            used_res.append(random.choice(res_set))
        # the length of critical and non-crit sections
        critical_len = 0
        for r in used_res:
            critical_len += r.length
        non_crit_len = random.randint(critical_len * alpha, critical_len * alpha * 2)
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


# INIT ===================================================================

# COMPONENTS
# generate resources and tasks
if SIMPLE_TASKS:
    res_set, task_set = gen_simple()
else:
    if TASK_RANDOM_SEED > 0:
        random.seed(TASK_RANDOM_SEED)
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
if MAP_RANDOM_SEED > 0:
    random.seed(MAP_RANDOM_SEED)
gen_task2core_map_safe(task_set, core_set)
# generate local ceiling table for each core
for c in core_set:
    gen_ceiling_table(c, res_set)

# instance launcher
launcher = Task_launcher(task_set)

# PIPELINE ===============================================================
print("\n[ START SIMULATION ]")
print("MrsP is {}".format("ON" if ENABLE_MRSP else "OFF"))
t = 0
start_time = time.time()
while t < T_MAX:
    new_insts = launcher.tick()

    # put the new insts into the pool of its corresponded core
    for inst in new_insts:
        inst.target_core.enroll(inst)
    
    # each core do sth
    for c in core_set:
        c.uptick() #0
    for c in core_set:
        c.intertick() #1
    for c in core_set:
        c.downtick() #0
    
    t += 1

print("\n[ SIMULATION RESULT ]")
for c in core_set:
    print(c.trace(100))
    print()

total_done = 0
total_resp = 0.0
for c in core_set:
    done_num, avg_resp = c.avg_resp_time()
    total_done += done_num
    total_resp += done_num * avg_resp
    print("core#{}\tavg_resp_time {:.5f}".format(c.idx, avg_resp))

print("\noverall\tavg_resp_time: {:.5f}\t num_of_migration: {}".format(total_resp/total_done, Core.MrsP_ctr))


print("\nsimulation time {}, for {} ticks".format(time.time() - start_time, T_MAX))