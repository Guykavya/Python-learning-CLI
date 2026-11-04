from collections import deque

n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

P = [0] * (n + 1)
for i in range(n):
    P[i + 1] = P[i] + a[i]

best = n + 1
dq = deque()        # start indices with increasing P values
# TODO: for i in 0..n: pop good starts from the front (record i - start), pop worse starts from the back, append i
print(best if best <= n else -1)
