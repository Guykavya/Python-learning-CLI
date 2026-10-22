from itertools import accumulate


def running_totals(numbers):
    return list(accumulate(numbers))


def running_max(numbers):
    return list(accumulate(numbers, max))
