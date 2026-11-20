# Custom node: max subarray sum in a range

A trader's profit per day is stored in a list; single days are corrected now and then. The question is: *what is the best total of consecutive days inside the period `[l, r)`?* That is the **maximum subarray sum** of `a[l:r]`, with updates. Write `BestRun` (chapter section 7). Ranges are **half-open and 0-indexed**.

- `BestRun(a)`;
- `update(i, v)`: `a[i] = v`;
- `best(l, r)`: the largest sum of a **non-empty** contiguous piece of `a[l:r]` (`l < r` always).

Each tree node must store a small record, `(total, best_prefix, best_suffix, best)`, and you must write the merge of two neighbouring records.

## Example

```python
>>> br = BestRun([2, -5, 4, -1, 3, -6, 5])
>>> br.best(0, 7), br.best(2, 5), br.best(0, 2), br.best(5, 7)
(6, 6, 2, 5)
>>> br.best(1, 2)                 # one negative element: the piece must not be empty
-5
>>> br.update(1, 10)
>>> br.best(0, 7)
18
```

## Constraints

- Values from `-10**9` to `10**9`; up to 10**5 elements and 10**5 operations.
- `O(log n)` per operation. Running Kadane's algorithm over the range is `O(r - l)`.

## Think about

1. The best piece of a joined range lies in the left part, in the right part, or **crosses the middle**. What do you need from each part to compute a crossing piece?
2. What is the record of a single element `v`, and why is its `best` not `max(v, 0)`?
3. The merge is not commutative. Where does that matter in your query?
