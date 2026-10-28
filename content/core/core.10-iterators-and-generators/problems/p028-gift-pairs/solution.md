## Approach

`combinations(items, 2)` gives every pair of two **different positions**, each pair only once,
earlier item first. That is exactly the set of choices. We keep the pairs whose prices add up
to the budget.

## Code

```python
from itertools import combinations


def gift_pairs(items, budget):
    return [
        (name1, name2)
        for (name1, price1), (name2, price2) in combinations(items, 2)
        if price1 + price2 == budget
    ]
```

## Complexity

O(n^2) time: there are n(n-1)/2 pairs. O(1) extra memory apart from the result.

## Another way

For large lists, a dictionary from price to the names seen so far finds pairs in O(n) on
average (the classic "two sum"). For a shop list of 20 items, `combinations` is clearer.
