import random
from tasks import *
from processor import *
from functools import reduce

# PARAMETERS ===============================================================
# simulation config
N_RES = 20              # number of resources
MIN_LEN = 10
MAX_LEN = 40
N_TASK = 10             # number of tasks
N_CORE = 8              # number of cores
ALPHA = 10              # length_of_noncritical / length_of_critical 

# processor profile
SWITCH_COST = 15        # cost of context switch


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
        for i in used_res:
            critical_len += used_res.length
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
        
        task_set.append(task(index, sections))
        print("task # {} consists of {}".format(index, sections))
    return task_set

def gen_cores(num):
    core_set = []
    for index in range(0, num):
        core_set.append(core(index))
    return core_set

def gen_task2core_map(tasks, cores):
    # a random mapper 
    mapping = {}
    for task in tasks:
        mapping[task.idx] = random.choice(cores)
    return mapping


# INIT ===================================================================
# COMPONENTS
res_set = gen_res(N_RES, MIN_LEN, MAX_LEN)
task_set = gen_tasks(N_TASK, res_set, ALPHA)
core_set = gen_cores(N_CORE)

# MODULES
feeder = task_launcher(task_set)
mapper = task_mapper(gen_task2core_map(task_set, core_set))