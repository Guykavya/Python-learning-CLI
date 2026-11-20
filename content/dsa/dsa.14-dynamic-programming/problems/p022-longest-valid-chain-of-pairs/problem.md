# Longest valid chain of pairs

Each pair `(a, b)` has `a < b`. A pair `(c, d)` may **follow** `(a, b)` in a chain only if `b < c` (strictly: touching pairs do not chain). You may pick the pairs in any order and skip any of them. Write `longest_chain(pairs)` that returns the length of the longest chain.

## Example

```python
>>> longest_chain([(1, 2), (2, 3), (3, 4)])     # (1,2) -> (3,4); (2,3) touches both
2
>>> longest_chain([(5, 24), (39, 60), (15, 28), (27, 40), (50, 90)])
3
>>> longest_chain([(1, 10), (2, 3), (4, 5)])     # starting with the earliest pair is wrong
2
>>> longest_chain([])
0
```

In the second example `(5, 24) -> (27, 40) -> (50, 90)` has length 3.

## Constraints

- `0 <= len(pairs) <= 1500`, values are integers (they may be negative), `a < b` in every pair.
- The input order means nothing: the pairs come shuffled.
- `O(n^2)` is fast enough. A recursion "longest chain starting with pair `i`" without a memo is exponential.

## Think about

Section 5 (maximum subarray) taught: if "the best among the first `i`" has no clear transition, add the condition "**and it ends with item `i`**", then take the max over all `i`. Use it here.

1. In which order must the pairs be listed so that every possible predecessor of a pair comes **before** it?
2. With that order, what is `f[i]` and which `j < i` may come right before pair `i`?
