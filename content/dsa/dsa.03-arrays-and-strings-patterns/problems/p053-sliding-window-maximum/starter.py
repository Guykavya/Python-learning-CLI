from collections import deque

n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

dq = deque()        # indices; their values decrease from front to back
out = []
# TODO: for each i: pop smaller-or-equal values from the back, append i, drop the front if it left the window,
#       and once i >= k - 1 record a[dq[0]]
print(*out)
