import random
def int_ripper(total, num_bins):
    splitter = []
    for i in range(0, num_bins-1):
        splitter.append(random.randint(0, total))
    splitter.sort()
    splitter = [0] + splitter + [total]
    bins = []
    for i in range(1, num_bins+1):
        bins.append(splitter[i] - splitter[i-1])
    return bins

def variance(num_list):
    avg = 0.0
    for n in num_list:
        avg += num_list
    avg = avg / len(num_list)

    v = 0.0
    for n in num_list:
        v += (v-n)**2
    return v / len(num_list)