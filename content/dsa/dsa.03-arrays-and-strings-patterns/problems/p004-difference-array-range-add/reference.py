n = int(input())
a = [int(x) for x in input().split()]
q = int(input())

d = [0] * (n + 2)
for _ in range(q):
    l, r, v = map(int, input().split())
    d[l] += v
    d[r + 1] -= v

run = 0
for i in range(1, n + 1):
    run += d[i]
    a[i - 1] += run

print(*a)
