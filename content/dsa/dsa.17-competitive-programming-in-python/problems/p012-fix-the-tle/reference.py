import sys
from collections import deque

data = sys.stdin.read().split()
q = int(data[0])
dq = deque()
out = []
pos = 1
for _ in range(q):
    op = data[pos]
    pos += 1
    if op == "push":
        dq.append(data[pos])
        pos += 1
    elif op == "pop":
        out.append(dq.popleft() if dq else "empty")
    else:
        out.append(str(len(dq)))
if out:
    print("\n".join(out))
