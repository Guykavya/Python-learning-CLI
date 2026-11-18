def max_lateness(jobs, order):
    t = 0
    worst = 0
    for i in order:
        duration, deadline = jobs[i]
        t += duration                      # finish time of job i
        worst = max(worst, t - deadline)
    return worst


def best_order(jobs):
    return sorted(range(len(jobs)), key=lambda i: jobs[i][1])
