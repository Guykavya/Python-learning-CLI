## Hint 1

How can you sort labels by their meaning rather than alphabetically? What number can stand for each label (its position in `order`)?

## Hint 2

```text
rank = {label: i for i, label in enumerate(order)}
for r in responses: if r not in rank: raise ValueError(...)
ranks = sorted(rank[r] for r in responses)
n = len(ranks); mid = n // 2
if n odd: return order[ranks[mid]]
lo, hi = ranks[mid - 1], ranks[mid]
return order[lo] if lo == hi else (order[lo], order[hi])
```
