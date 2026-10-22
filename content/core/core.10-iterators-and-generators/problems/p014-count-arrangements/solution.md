## Approach

The three functions are lazy. Counting one by one with a generator expression keeps memory flat. Note `k = 0` gives exactly one tuple, the empty tuple `()`, in all three, and `k` larger than the number of items gives none for permutations and combinations (but `product` with repeats still works).

## Code

```python
from itertools import combinations, permutations, product


def count_arrangements(items, k):
    return {
        "product": sum(1 for _ in product(items, repeat=k)),
        "permutations": sum(1 for _ in permutations(items, k)),
        "combinations": sum(1 for _ in combinations(items, k)),
    }
```

## Complexity

Time is proportional to the number of tuples produced, which grows quickly (n^k for product). Memory is O(1).

## Another way

The formulas are n^k, n!/(n-k)! and n!/(k!(n-k)!), but running the iterators teaches you what they actually produce, and gives the same numbers.
