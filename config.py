# PARAMETERS ===============================================================
SIMPLE_TASKS = True
ENABLE_MRSP = True

N_CORE = 4              # number of cores
T_MAX = 1000

TASK_RANDOM_SEED = 32767
MAP_RANDOM_SEED = 961

# simulation config
N_RES = 2              # number of resources
MIN_LEN = 5
MAX_LEN = 20
N_TASK = 10             # number of tasks
ALPHA = 1              # length_of_noncritical / length_of_critical 
UTILIZATION = N_CORE / N_TASK / 1.5

# processor profile
SWITCH_COST = 1        # cost of context switch
MAX_PRI = 32767

# snippet types:
STYPE_NON_CRIT = 1
STYPE_CRITICAL = 2
STYPE_SWITCH = 3