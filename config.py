# PARAMETERS ===============================================================
SIMPLE_TASKS = True
ENABLE_MRSP = False

N_CORE = 2              # number of cores
T_MAX = 500000

# simulation config
N_RES = 20              # number of resources
MIN_LEN = 5
MAX_LEN = 40
N_TASK = 10             # number of tasks
ALPHA = 2              # length_of_noncritical / length_of_critical 
UTILIZATION = N_CORE / N_TASK 

# processor profile
SWITCH_COST = 1        # cost of context switch
MAX_PRI = 32767

# snippet types:
STYPE_NON_CRIT = 1
STYPE_CRITICAL = 2
STYPE_SWITCH = 3