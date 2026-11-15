from collections import deque

n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

dq = deque()        # indices; their values decrease from front to back
out = []
for i in range(n):
    while dq and a[dq[-1]] <= a[i]:
        dq.pop()                    # a[i] is at least as big and stays longer
    dq.append(i)
    if dq[0] <= i - k:
        dq.popleft()                # the front has left the window
    if i >= k - 1:
        out.append(a[dq[0]])
print(*out)
