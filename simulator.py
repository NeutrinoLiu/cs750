import random
import math
import time
from config import *
from simple_tasks import gen_simple
from tasks import Task, Res
from processor import Core, Task_launcher
from utils import int_ripper
from random_opt import gen_task2core_map_random_opt

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
        num_used_res = random.randint(0, len(res_set) * 2)
        used_res = []
        for i in range(0, num_used_res):
            used_res.append(random.choice(res_set))
        # the length of critical and non-crit sections
        critical_len = 0
        for r in used_res:
            critical_len += r.length
        if critical_len == 0:
            non_crit_len = random.randint(MIN_LEN, MAX_LEN * (ALPHA + 1))
        else:
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
    if MAP_RANDOM_SEED > 0:
        random.seed(MAP_RANDOM_SEED)
    else:
        seed = time.time()
        mprint("MAP RANDOM SEED is {}".format(seed))
        random.seed(seed)
    for t in tasks:
        target_core = random.choice(cores)
        while target_core.utilization + t.utilization > 1:
            target_core = random.choice(cores)
        target_core.affi_tasks.append(t)
        t.target_core = target_core
    if PRINT_MAP:
        mprint("\n[ TASK-CORE MAP ]")
        for c in cores:
            mprint(c)
        
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

def mprint(content):
    if MY_PRINT:
        print(content)

def one_time_simulation(task_rand_seed):

    # INIT ===================================================================
    # COMPONENTS
    # generate resources and tasks
    if SIMPLE_TASKS:
        res_set, task_set = gen_simple()
    else:
        if task_rand_seed > 0:
            random.seed(task_rand_seed)
        else:
            seed = time.time()
            mprint("TASK RANDOM SEED is {}".format(seed))
            random.seed(seed)
        res_set = gen_res(N_RES, MIN_LEN, MAX_LEN)
        task_set = gen_tasks(N_TASK, res_set, ALPHA)

    # generate priority according to the period
    gen_priority(task_set)
    if PRINT_TASK:
        mprint("\n[ TASK STRUCTURE ]")
        for t in task_set:
            mprint(t)

    # RTS MODULES
    # generate cores
    core_set = gen_cores(N_CORE)

    # maps between task and core
    if OPTIMAL_MAP:
        gen_task2core_map_random_opt(task_set, core_set, res_set)
    else:
        gen_task2core_map_safe(task_set, core_set)

    # generate local ceiling table for each core
    for c in core_set:
        gen_ceiling_table(c, res_set)

    # instance launcher
    launcher = Task_launcher(task_set)

    # PIPELINE ===============================================================
    mprint("\n[ START SIMULATION ]")
    mprint("MrsP is {}".format("ON" if ENABLE_MRSP else "OFF"))
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

    mprint("\n[ SIMULATION RESULT ]")

    total_done = 0
    total_resp = 0.0
    total_top_done = 0
    total_top_resp = 0.0
    total_bot_resp = 0.0
    total_bot_done = 0
    for c in core_set:
        done_num, avg_resp = c.avg_resp_time()
        top_pri_done, top_pri_resp = c.avg_resp_time_top()
        bot_pri_done, bot_pri_resp = c.avg_resp_time_bot()
        total_done += done_num
        total_top_done += top_pri_done
        total_bot_done += bot_pri_done
        total_resp += done_num * avg_resp
        total_top_resp += top_pri_done * top_pri_resp
        total_bot_resp += bot_pri_done * bot_pri_resp
        if PRINT_PERCORE:
            mprint("core#{}\tavg_resp_time {:.5f}".format(c.idx, avg_resp))

    mprint("top_resp_time: {:.5f} for {} instances \nbot_resp_time: {:.5f} for {} instances \nnum_of_migration: {} \navg_resp_time: {:.5f} for {} instances".format(total_top_resp/total_top_done, total_top_done, total_bot_resp/total_bot_done, total_bot_done, Core.MrsP_ctr, total_resp/total_done, total_done))
    mprint("\nsimulation time {}, for {} ticks".format(time.time() - start_time, T_MAX))

    return total_top_resp/total_top_done, total_bot_resp/total_bot_done, Core.MrsP_ctr, total_resp/total_done

for i in range(0, 200):
    with open("data.txt", "a") as f:
        Core.rst_ctr()
        try:
            top_avg, bot_avg, ctr, total_avg = one_time_simulation(i + 10086)
        except Exception:
            f.write("ddl passed\n")
        else: 
            f.write("{:.2f}\t{:.2f}\t{}\t{:.2f}\n".format(top_avg, bot_avg, ctr, total_avg))
