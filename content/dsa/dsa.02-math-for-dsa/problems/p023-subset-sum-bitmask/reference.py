n, t = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

sums = [0] * (1 << n)
count = 1 if t == 0 else 0
for mask in range(1, 1 << n):
    low = mask & -mask
    sums[mask] = sums[mask ^ low] + a[low.bit_length() - 1]
    if sums[mask] == t:
        count += 1
print(count)
