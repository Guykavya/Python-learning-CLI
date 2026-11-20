# Mo's algorithm

A library has the list of book genres on a long shelf, numbered `0` to `n - 1`. Visitors ask many questions at once: *how many different genres stand on shelf positions `[l, r)`?* The shelf never changes and all questions are known in advance. Write `distinct_counts(a, queries)` that returns the answers in the order of `queries`, using Mo's algorithm (chapter section 16). Ranges are **half-open and 0-indexed**, `l <= r`.

## Example

```python
>>> distinct_counts([4, 7, 4, 4, 9, 7], [(0, 6), (0, 3), (2, 5), (1, 2), (3, 6), (2, 2)])
[3, 2, 2, 1, 3, 0]
```

## Constraints

- Up to 5 * 10**4 genres (`0 <= a[i] <= 10**6`) and 5 * 10**4 questions.
- `len(set(a[l:r]))` per question is `O(n)` each, about 10**9 steps for the tests.

## Think about

1. Keep a window `[cur_l, cur_r)` with a count per genre and the number of genres with a positive count. What does adding one element change? Removing one?
2. In which order should the questions be processed so that the window moves little in total? Why sort by `(l // B, r)`?
3. Why must the window **grow before it shrinks**?
