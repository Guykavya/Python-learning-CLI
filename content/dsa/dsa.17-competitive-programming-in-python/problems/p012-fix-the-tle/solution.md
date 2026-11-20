## Approach

```python
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
```

The three changes: `input()` per line to `read().split()`, `list.pop(0)` to `deque.popleft()`, one `print` per answer to one `print` at the end. The values stay strings in the deque because they are only echoed back (but `int` would also be correct).

## Complexity

`O(q)` instead of `O(q * n)` for the list version: `pop(0)` shifts every remaining element left, so with 200 000 elements in the list every pop moves about 200 000 pointers.

## Another way

Keep a list and a `head` index: `pop` reads `a[head]` and does `head += 1`. It is the same idea (never move elements) and needs no import.
