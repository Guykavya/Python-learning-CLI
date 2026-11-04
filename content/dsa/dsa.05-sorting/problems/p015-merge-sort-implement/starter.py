import sys
sys.setrecursionlimit(10000)

n = int(input())
a = [int(x) for x in input().split()]


def merge_sort(a):
    # TODO: split, sort the halves recursively, merge
    return a


print(" ".join(map(str, merge_sort(a))))
