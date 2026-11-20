def count_strings(n, k):
    # t[i][run] = ways to finish when i characters are left and the string ends in `run` ones
    t = [[0] * k for _ in range(n + 1)]
    for run in range(k):
        t[0][run] = 1                                  # base case: nothing left to place
    for i in range(1, n + 1):
        for run in range(k):
            total = t[i - 1][0]                        # place a 0
            if run + 1 < k:
                total += t[i - 1][run + 1]             # place a 1
            t[i][run] = total
    return t[n][0]
