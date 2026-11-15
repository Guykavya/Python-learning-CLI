# k-th permutation without generating them all

The permutations of the digits `1 .. n` are listed in lexicographic (dictionary) order and numbered from 1. For `n = 3`:

```text
1: 123   2: 132   3: 213   4: 231   5: 312   6: 321
```

Write `kth_permutation(n, k)` that returns the `k`-th one as a string, **without generating the permutations before it**.

## Example

```python
>>> kth_permutation(3, 3)
'213'
>>> kth_permutation(4, 9)
'2314'
>>> kth_permutation(1, 1)
'1'
```

## Constraints

- `1 <= n <= 9`, `1 <= k <= n!`
- The tests ask hundreds of queries with `n = 9`; generating up to 362,880 permutations for each one is too slow.

## Think about

How many permutations start with `1`? With `2`? If `k = 9` and `n = 4`, in which block of `3! = 6` does the 9th permutation lie, and what is its first digit?
