from collections import deque

n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

P = [0] * (n + 1)
for i in range(n):
    P[i + 1] = P[i] + a[i]

best = n + 1
dq = deque()        # start indices with increasing P values
for i in range(n + 1):
    while dq and P[i] - P[dq[0]] >= k:
        best = min(best, i - dq.popleft())   # later ends can only be longer for this start
    while dq and P[dq[-1]] >= P[i]:
        dq.pop()                             # i is a later start with a smaller-or-equal prefix: always better
    dq.append(i)
print(best if best <= n else -1)
