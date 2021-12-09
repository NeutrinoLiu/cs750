import math
import random
import time

from config import *

def distance(list_a, list_b):
    dist = 0.0
    length = min(len(list_a), len(list_b))
    for i in range(0, length):
        dist += (list_a[i] - list_b[i]) ** 2
    return math.sqrt(dist)

def avg_distance(vector_list):
    num_vector = len(vector_list)
    sum_dist = 0.0
    for i in range(0, num_vector-1):
        for j in range(i+1, num_vector):
            sum_dist += distance(vector_list[i], vector_list[j])
    return sum_dist / ( num_vector * (num_vector - 1) / 2 ) 

def gen_big_vector(task_list, res_set):
    dimension_values = {}
    for r in res_set:
        dimension_values[r.idx] = 0.0
    for t in task_list:
        for r in t.used_res:
            dimension_values[r.idx] += 1/t.period
    return list(dimension_values.values())

def compute_cost(group_lists, res_set):
    big_vector_list = []
    for g in group_lists:
        big_vector_list.append(gen_big_vector(g, res_set))
    return avg_distance(big_vector_list)

def gen_random_map(core_set, task_set):
    bins = len(core_set)
    all_bins = []
    for i in range(0, bins):
        all_bins.append([])
    for t in task_set:
        target_bin = random.choice(all_bins)
        target_bin.append(t)
    return all_bins

def mprint(content):
    if MY_PRINT:
        print(content)

def gen_task2core_map_random_opt(task_set, core_set, res_set):
    optimal_value = None
    optimal_map = None

    mprint("\n[ RANDOM OPTIMIZER ]")
    start_time = time.time()
    if MAP_RANDOM_SEED > 0:
        random.seed(MAP_RANDOM_SEED)
    else:
        random.seed(time.time())

    for r in range(0, RAND_OPT_ROUNDS):
        group_lists = gen_random_map(core_set, task_set)
        # group list is a list of list<tasks>
        # e.g. [  [t1,t2], [t0], [t4]  ]
        cur_cost = compute_cost(group_lists, res_set)
        if optimal_value == None:
            optimal_map = group_lists
            optimal_value = cur_cost
        elif optimal_value > cur_cost:
            optimal_map = group_lists
            optimal_value = cur_cost
    
    mprint("{} used to run random optimizer for {} iterations".format(time.time() - start_time, RAND_OPT_ROUNDS))
    mprint("min avg distance between cores: {:.5f}".format(optimal_value))
    
    for c in core_set:
        local_task_list = optimal_map[c.idx]
        c.affi_tasks = local_task_list
        for t in local_task_list:
            t.target_core = c
        if PRINT_MAP:
            mprint(c)