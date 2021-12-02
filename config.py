# PARAMETERS ===============================================================
SIMPLE_TASKS = False

# simulation config
N_RES = 20              # number of resources
MIN_LEN = 5
MAX_LEN = 40
N_TASK = 10             # number of tasks
N_CORE = 1              # number of cores
ALPHA = 10              # length_of_noncritical / length_of_critical 
UTILIZATION = N_CORE / N_TASK
T_MAX = 5000000

# processor profile
SWITCH_COST = 1        # cost of context switch
MAX_PRI = 32767

# snippet types:
STYPE_NON_CRIT = 1
STYPE_CRITICAL = 2
STYPE_SWITCH = 3