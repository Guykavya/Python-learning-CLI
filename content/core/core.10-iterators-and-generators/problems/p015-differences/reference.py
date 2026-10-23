from itertools import pairwise


def differences(numbers):
    return [b - a for a, b in pairwise(numbers)]
