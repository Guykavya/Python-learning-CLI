## Approach

Work with distinct **values**, not positions. For each value `a`, the partner is `target - a`.
A set answers "is the partner here?" in O(1). The only special case is `a == b`, which needs
the value to appear at least twice.

## Code

```python
nums = [int(x) for x in input().split()]
target = int(input())
counts = {}
for x in nums:
    counts[x] = counts.get(x, 0) + 1
pairs = []
for a in counts:
    b = target - a
    if a < b and b in counts:
        pairs.append((a, b))
    elif a == b and counts[a] >= 2:
        pairs.append((a, b))
pairs.sort()
for a, b in pairs:
    print(f"{a} + {b}")
print("Pairs:", len(pairs))
```

## Complexity

O(n) to build the set and counts, plus O(p log p) to sort p pairs. Two nested loops over
positions would be O(n²).
