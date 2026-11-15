# Fix the slow combination sum

`starter.py` contains a **correct but slow** `combination_sum(candidates, target, counter)` (each distinct positive candidate may be used any number of times, as in problem 21). It finds the right answers, but it makes far too many recursive calls: it only notices that it overshot the target **after** it has already made the call.

Fix it with the pruning from chapter section 9:

1. sort the candidates;
2. before recursing, check whether the candidate still fits; because the list is sorted, the first candidate that is too big ends the loop with `break`.

The tests pass a `counter` object. Keep the line `counter.tick()` as the first line of `go`: it counts every call, and the tests fail if the count is far above what a pruned search needs. Do not change the parameters or the answers.

## Example

```python
>>> combination_sum([2, 3, 6, 7], 7, counter)
[[2, 2, 3], [7]]
```

For candidates `[2, 3]` plus the odd numbers 41 .. 89 (27 numbers) and target 120, the starter makes 207,884 calls; a pruned version makes about 12,000 for the same 568 answers.

## Think about

Each call of the starter that ends in `if remaining < 0: return` is a wasted node of the tree. Where should the check happen so that such a node is never created?
