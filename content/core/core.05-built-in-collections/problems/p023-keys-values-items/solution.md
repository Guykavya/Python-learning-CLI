## Approach

`keys()`, `values()` and `items()` all follow insertion order, so they line up. `max` with
`key=d.get` compares the keys by their values.

## Code

```python
scores = {}
for _ in range(int(input())):
    name, score = input().split()
    scores[name] = int(score)
print("Names:", " ".join(scores.keys()))
print("Scores:", " ".join(str(v) for v in scores.values()))
print("Total:", sum(scores.values()))
best = max(scores, key=scores.get)
print(f"Best: {best} ({scores[best]})")
```

## Complexity

O(n) for everything here.

## Another way

Without `key=`, loop over `d.items()` and keep the best pair, replacing it only on a strictly
greater score.
