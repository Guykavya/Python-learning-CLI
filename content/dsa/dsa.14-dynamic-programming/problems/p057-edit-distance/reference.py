def edit_distance(a, b):
    prev = list(range(len(b) + 1))               # row 0: f[0][j] = j inserts
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)                 # f[i][0] = i deletes
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1]             # keep it, no cost
            else:
                cur[j] = 1 + min(prev[j - 1],    # replace
                                 prev[j],        # delete a[i-1]
                                 cur[j - 1])     # insert b[j-1]
        prev = cur
    return prev[-1]
