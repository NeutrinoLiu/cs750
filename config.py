# PARAMETERS ===============================================================
SIMPLE_TASKS = False
ENABLE_MRSP = True
RANDOM_SEED = 32773

N_CORE = 2              # number of cores
T_MAX = 10000

# simulation config
N_RES = 2              # number of resources
MIN_LEN = 50
MAX_LEN = 100
N_TASK = 10             # number of tasks
ALPHA = 1              # length_of_noncritical / length_of_critical 
UTILIZATION = N_CORE / N_TASK / 2

# processor profile
SWITCH_COST = 1        # cost of context switch
MAX_PRI = 32767

# snippet types:
STYPE_NON_CRIT = 1
STYPE_CRITICAL = 2
STYPE_SWITCH = 3