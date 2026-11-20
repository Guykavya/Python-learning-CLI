def max_profit(jobs):
    n = len(jobs)
    free = [True] * (n + 1)                    # free[1..n]; slot 0 is unused
    total = 0
    for deadline, profit in sorted(jobs, key=lambda j: -j[1]):
        for t in range(min(deadline, n), 0, -1):   # latest free slot first
            if free[t]:
                free[t] = False
                total += profit
                break
    return total
