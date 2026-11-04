n = int(input())
a = [int(x) for x in input().split()]
# TODO: one pass with three pointers low, mid, high; swap 0s to the front and 2s to the back
print(" ".join(map(str, a)))
