# Minimum waiting time

A print shop has one printer and a queue of jobs; job `i` takes `durations[i]` minutes. A job's **waiting time** is the total duration of the jobs printed **before** it (the first job waits 0). Write `min_total_waiting(durations)`: the smallest possible **sum of waiting times** over all orders of the jobs.

Rules (chapter section 10):

- `durations` is a list of non-negative integers, in any order. Return an `int`. An empty list gives `0`.
- Do not change the list you are given.

## Example

```python
>>> min_total_waiting([6, 8, 7, 3])
28
>>> min_total_waiting([2, 1, 3])
4
>>> min_total_waiting([5])
0
```

For `[6, 8, 7, 3]` the best order is `3, 6, 7, 8`: the jobs wait `0, 3, 9, 16`, total 28. Printing them as given costs 41.

## Constraints

- `0 <= len(durations) <= 10**5`. Trying all orders is `n!`; aim for `O(n log n)`.

## Think about

Two neighbouring jobs, a long one just before a short one. Swap them: who waits less, who waits more, and does anyone **outside** the pair notice?
