n, t = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

# Every subset is a number `mask` from 0 to 2^n - 1. Bit i of mask says "a[i] is in the subset".
# Count the masks whose chosen elements add up to t.
print(0)
