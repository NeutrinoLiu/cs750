# PARAMETERS ===============================================================
SIMPLE_TASKS = False
ENABLE_MRSP = True

OPTIMAL_MAP = True
RAND_OPT_ROUNDS = 10000


N_CORE = 4              # number of cores
T_MAX = 100000

TASK_RANDOM_SEED = 1639012615
MAP_RANDOM_SEED = 32767

# simulation config
N_RES = 4              # number of resources
MIN_LEN = 5
MAX_LEN = 20
N_TASK = 16             # number of tasks
ALPHA = 1              # length_of_noncritical / length_of_critical 
UTILIZATION = N_CORE / N_TASK / 1.8

# processor profile
SWITCH_COST = 1        # cost of context switch
MAX_PRI = 32767

# snippet types:
STYPE_NON_CRIT = 1
STYPE_CRITICAL = 2
STYPE_SWITCH = 3

# print config
MY_PRINT = False
PRINT_TASK = False
PRINT_MAP = False
PRINT_PERCORE = False

# MACRO repeats
TOTAL_SIMULATIONS = 100