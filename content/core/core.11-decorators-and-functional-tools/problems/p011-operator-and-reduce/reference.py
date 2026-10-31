from functools import reduce
from operator import itemgetter, mul


def sort_by_price(items):
    return sorted(items, key=itemgetter(1))


def sort_people(people):
    return sorted(people, key=itemgetter("city", "age"))


def product(nums):
    return reduce(mul, nums, 1)


def largest(nums):
    if not nums:
        raise ValueError("largest() of an empty list")
    return reduce(lambda best, x: x if x > best else best, nums)
