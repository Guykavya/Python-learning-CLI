MOD = 10 ** 9 + 7


def sum_subarray_mins(arr):
    # TODO: contribution technique with two monotonic-stack passes
    return sum(arr) % MOD
