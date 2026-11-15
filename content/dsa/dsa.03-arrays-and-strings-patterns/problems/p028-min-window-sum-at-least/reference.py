n, s = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

best = n + 1                 # "no window found yet": longer than any real window
total = 0
l = 0
for r in range(n):
    total += a[r]
    while total >= s:        # the window a[l..r] is good: record it, then try to shrink it
        if r - l + 1 < best:
            best = r - l + 1
        total -= a[l]
        l += 1

print(best if best <= n else 0)
