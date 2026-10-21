## Approach

Count with a dict, sort tuples for the table, and find everyone who has the maximum.

## Code

```python
n = int(input())
counts = {}
for _ in range(n):
    name = input().strip()
    counts[name] = counts.get(name, 0) + 1
if not counts:
    print("No votes")
else:
    for neg, name in sorted((-v, name) for name, v in counts.items()):
        print(f"{name}: {-neg}")
    best = max(counts.values())
    leaders = sorted(name for name, v in counts.items() if v == best)
    if len(leaders) == 1:
        print("Winner:", leaders[0])
    else:
        print("Tie:", ", ".join(leaders))
```

## Complexity

O(n) counting plus O(k log k) sorting for k candidates.
