from collections import Counter


def least_interval(tasks, n):
    if not tasks:
        return 0
    counts = Counter(tasks)
    f = max(counts.values())
    m = sum(1 for c in counts.values() if c == f)
    return max(len(tasks), (f - 1) * (n + 1) + m)
