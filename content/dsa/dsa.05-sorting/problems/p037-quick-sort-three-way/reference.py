import random

n = int(input())
a = [int(x) for x in input().split()]


def quick(a):
    if len(a) <= 1:
        return a
    pivot = a[random.randrange(len(a))]
    less = [x for x in a if x < pivot]
    equal = [x for x in a if x == pivot]
    greater = [x for x in a if x > pivot]
    return quick(less) + equal + quick(greater)


print(" ".join(map(str, quick(a))))
