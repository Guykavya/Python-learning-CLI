# count_arrangements: product, permutations, combinations

Write `count_arrangements(items, k)` in `solution.py`. It returns a dict with three entries, each the
**number** of tuples that `itertools` produces:

- `"product"`: `product(items, repeat=k)` (choose `k` times, repetition allowed, order matters)
- `"permutations"`: `permutations(items, k)` (no repetition, order matters)
- `"combinations"`: `combinations(items, k)` (no repetition, order does not matter)

Count by really running the iterators, for example `sum(1 for _ in ...)`. Do not use `math`.

**Examples**

```python
count_arrangements("abc", 2)
# {"product": 9, "permutations": 6, "combinations": 3}
count_arrangements("abc", 0)
# {"product": 1, "permutations": 1, "combinations": 1}
count_arrangements("ab", 3)
# {"product": 8, "permutations": 0, "combinations": 0}
```
