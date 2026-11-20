import math


def distinct_counts(a, queries):
    n = len(a)
    B = max(1, math.isqrt(n))
    order = sorted(range(len(queries)),
                   key=lambda i: (queries[i][0] // B,
                                  queries[i][1] if (queries[i][0] // B) % 2 == 0 else -queries[i][1]))
    count = {}
    distinct = 0
    cur_l = cur_r = 0                        # the window a[cur_l:cur_r], empty at first
    answers = [0] * len(queries)
    for qi in order:
        l, r = queries[qi]
        while cur_l > l:                     # grow first ...
            cur_l -= 1
            x = a[cur_l]
            count[x] = count.get(x, 0) + 1
            distinct += count[x] == 1
        while cur_r < r:
            x = a[cur_r]
            count[x] = count.get(x, 0) + 1
            distinct += count[x] == 1
            cur_r += 1
        while cur_l < l:                     # ... then shrink
            x = a[cur_l]
            count[x] -= 1
            distinct -= count[x] == 0
            cur_l += 1
        while cur_r > r:
            cur_r -= 1
            x = a[cur_r]
            count[x] -= 1
            distinct -= count[x] == 0
        answers[qi] = distinct
    return answers
