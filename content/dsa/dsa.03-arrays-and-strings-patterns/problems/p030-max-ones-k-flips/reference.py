n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

l = 0
zeros = 0            # zeros inside the window a[l..r]: the flips it needs
best = 0
for r in range(n):
    if a[r] == 0:
        zeros += 1
    while zeros > k:     # too many flips needed: shrink from the left
        if a[l] == 0:
            zeros -= 1
        l += 1
    if r - l + 1 > best:
        best = r - l + 1

print(best)
