n = int(input())
h = [int(x) for x in input().split()]

l, r = 0, n - 1
best = 0
while l < r:
    area = min(h[l], h[r]) * (r - l)
    if area > best:
        best = area
    if h[l] < h[r]:
        l += 1          # the shorter wall limits every container that keeps it: drop it
    else:
        r -= 1
print(best)
