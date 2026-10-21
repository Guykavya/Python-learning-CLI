## Approach

Decorate, sort, undecorate. Build `(-score, name)` tuples so a plain ascending sort gives the
order we want, then take the first three with a slice (which is safe if there are fewer).

## Code

```python
n = int(input())
ranked = []
for _ in range(n):
    name, score = input().split()
    ranked.append((-int(score), name))
ranked.sort()
if not ranked:
    print("No scores.")
for place, (neg, name) in enumerate(ranked[:3], start=1):
    print(f"{place}. {name} {-neg}")
```

## Complexity

O(n log n) for the sort.

## Another way: sort twice

Because sorting is stable, sort by the secondary key first, then by the primary key:
sort the names alphabetically, then sort by score with `reverse=True`. With `lambda` (core.06)
that is `sorted(sorted(people), key=lambda p: p[1], reverse=True)`.
