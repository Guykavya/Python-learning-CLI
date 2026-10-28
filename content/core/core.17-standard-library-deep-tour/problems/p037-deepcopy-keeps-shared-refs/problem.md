# Trace: deepcopy keeps the shape of sharing

A common belief is "after `deepcopy`, nothing is shared any more". That is half true. `deepcopy`
shares nothing **with the original**, but inside the copy it rebuilds the same **shape**: if one
object appears twice in the original, its copy appears twice in the result. It does that with
the `memo` dict: `memo[id(original)] = copy`. Before copying any object, `deepcopy` looks it up
in `memo`; if it has already been copied during this call, it reuses that copy. The same trick
makes cycles (an object that contains itself) work.

Predict **every line** this program prints:

```python
import copy

shared = [0]
box = {"a": shared, "b": shared}
c = copy.deepcopy(box)
c["a"].append(1)
print("A", c["b"])
print("B", shared)
print("C", c["a"] is c["b"], c["a"] is shared)

grid = [[0] * 2] * 2
g2 = copy.deepcopy(grid)
g2[0][0] = 7
print("D", g2)
print("E", grid)

loop = [1]
loop.append(loop)
lc = copy.deepcopy(loop)
print("F", lc[1] is lc, lc is loop)
print("G", lc)

memo = {}
x = [1, 2]
first = copy.deepcopy(x, memo)
second = copy.deepcopy(x, memo)
print("H", first is second, first is x)

pair = (shared, shared)
p2 = copy.deepcopy(pair)
print("I", p2[0] is p2[1], p2 is pair)


class Node:
    def __init__(self, name):
        self.name = name
        self.peers = []


a = Node("a")
b = Node("b")
a.peers.append(b)
b.peers.append(a)
a2 = copy.deepcopy(a)
print("J", a2.peers[0].name, a2.peers[0].peers[0] is a2, a2.peers[0] is b)

s = copy.copy([shared, shared])
d = copy.deepcopy([shared, [shared]])
print("K", s[0] is shared, d[0] is d[1][0], d[0] is shared)
```

`print` shows a list that contains itself as `[...]` at the point where it would repeat.

Write your answer in `answer.txt`, one printed line per line.

**Example** (one line, given away):

```text
B [0]
```
