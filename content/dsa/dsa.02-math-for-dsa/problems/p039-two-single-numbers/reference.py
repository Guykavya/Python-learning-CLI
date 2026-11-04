n = int(input())
values = [int(v) for v in input().split()]

x = 0
for v in values:
    x ^= v
low = x & -x
a = 0
b = 0
for v in values:
    if v & low:
        a ^= v
    else:
        b ^= v
print(min(a, b), max(a, b))
