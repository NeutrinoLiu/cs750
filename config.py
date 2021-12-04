# PARAMETERS ===============================================================
SIMPLE_TASKS = False
ENABLE_MRSP = False
OPTIMAL_MAP = True

N_CORE = 8              # number of cores
T_MAX = 100000

TASK_RANDOM_SEED = 314159
MAP_RANDOM_SEED = 0

# simulation config
N_RES = 8              # number of resources
MIN_LEN = 5
MAX_LEN = 20
N_TASK = 20             # number of tasks
ALPHA = 1              # length_of_noncritical / length_of_critical 
UTILIZATION = N_CORE / N_TASK / 2

# processor profile
SWITCH_COST = 1        # cost of context switch
MAX_PRI = 32767

# snippet types:
STYPE_NON_CRIT = 1
STYPE_CRITICAL = 2
STYPE_SWITCH = 3