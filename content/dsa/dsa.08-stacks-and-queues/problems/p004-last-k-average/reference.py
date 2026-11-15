from collections import deque


def moving_averages(values, k):
    window = deque(maxlen=k)
    total = 0
    out = []
    for x in values:
        if len(window) == k:
            total -= window[0]
        window.append(x)
        total += x
        out.append(total / len(window))
    return out
