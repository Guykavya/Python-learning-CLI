from functools import reduce


def group_by(items, key):
    def step(groups, item):
        k = key(item)
        return {**groups, k: groups.get(k, []) + [item]}
    return reduce(step, items, {})


def count_by(items, key):
    def step(counts, item):
        k = key(item)
        return {**counts, k: counts.get(k, 0) + 1}
    return reduce(step, items, {})


def merge_counts(*counts):
    def merge_two(total, more):
        result = dict(total)
        for k, n in more.items():
            result[k] = result.get(k, 0) + n
        return result
    return reduce(merge_two, counts, {})
