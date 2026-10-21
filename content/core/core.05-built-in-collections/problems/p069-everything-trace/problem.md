# Collections all together

Predict **exactly** what this program prints, one line per printed line. Do not run it.
It mixes everything from this module, so go slowly and draw what you need.

```python
data = ["b3", "a1", "c2", "a2"]
groups = {}
for item in data:
    groups.setdefault(item[0], []).append(int(item[1]))
print(groups)
keys = groups.keys()
groups["d"] = []
print(len(keys), list(keys))
totals = {k: sum(v) for k, v in groups.items() if v}
print(totals)
ranked = sorted((-v, k) for k, v in totals.items())
print(ranked)
matrix = [[0] * 2 for _ in range(2)]
alias = matrix[0]
alias.append(9)
snapshot = [row[:] for row in matrix]
matrix[1][0] = 5
print(matrix, snapshot)
s = {x % 4 for x in range(10)}
t = frozenset([1, 2, 5])
print(sorted(s & t), sorted(s ^ t))
flat = [x for row in matrix for x in row if x]
print(flat)
first, *rest = sorted(flat, reverse=True)
print(first, rest)
```

Write your answer in `answer.txt`.
