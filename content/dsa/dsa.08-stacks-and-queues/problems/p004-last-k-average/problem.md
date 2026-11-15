# Average of the last k values

A sensor sends one number at a time. After each number, you report the average of the **last `k` numbers** received so far. Before `k` numbers have arrived, average all of them.

Write `moving_averages(values, k)` that returns the list of these averages, one per value, as floats.

Use a `deque(maxlen=k)` for the window (chapter section 4, "The average of the last k values") and a **running total**: when the window is full, subtract the value that is about to be dropped, then add the new one. Do not call `sum(window)` for every value: with a large `k` that is `O(k)` per value, and the last test (100,000 values, `k = 50,000`) has a time limit.

## Example

```python
>>> moving_averages([1, 10, 3, 5], 3)
[1.0, 5.5, 4.666666666666667, 6.0]
>>> moving_averages([4, 8], 5)
[4.0, 6.0]
>>> moving_averages([], 2)
[]
```

`[1, 10, 3, 5]` with `k = 3`: after 1 the window is `[1]` (average 1.0); after 10 it is `[1, 10]` (5.5); after 3 it is `[1, 10, 3]` (14 / 3); after 5 the 1 is dropped and the window is `[10, 3, 5]` (6.0).

## Constraints

- `1 <= k`, `0 <= len(values) <= 10**5`; the values are integers.
- The tests compare your averages with a tolerance of `1e-9`, so small float rounding differences are fine.

## Think about

In which order must "subtract the oldest" and `append` happen? What goes wrong if you append first?
