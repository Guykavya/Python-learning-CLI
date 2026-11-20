from functools import cmp_to_key


def largest_number(nums):
    strs = [str(x) for x in nums]

    def compare(a, b):
        if a + b > b + a:
            return -1            # a comes first
        if a + b < b + a:
            return 1
        return 0

    strs.sort(key=cmp_to_key(compare))
    result = "".join(strs)
    return "0" if result[0] == "0" else result      # [0, 0] -> "0", not "00"
