# Fix the knapsack

A delivery app packs a drone. Every parcel can be loaded **at most once**, the drone carries total weight `capacity`, and the app wants the largest total value. A teammate saved memory with the one-array knapsack (chapter section 10). The code is in `starter.py`:

```python
def knapsack(weights, values, capacity):
    """0/1 knapsack: each parcel at most once. Return the best total value."""
    best = [0] * (capacity + 1)
    for i in range(len(weights)):
        for c in range(weights[i], capacity + 1):
            best[c] = max(best[c], best[c - weights[i]] + values[i])
    return best[capacity]
```

The tests pass on most small cases, but a customer reports this:

```python
>>> knapsack([2], [10], 7)          # one parcel, weight 2, value 10
30                                  # the starter: the drone carries the same parcel 3 times
10                                  # expected
>>> knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7)
9                                   # both: here the bug happens to give the right answer
```

1. Trace `best` for the first call by hand. Which cell does `best[4]` read, and what does that cell already contain when it is read?
2. Explain in one sentence what problem the starter really solves.
3. Fix the function. Keep the signature and keep the memory at **one array** of size `capacity + 1` (no 2-D table).

## Rules for the fixed function

- `weights[i] >= 1`, `values[i] >= 0`, `0 <= capacity <= 10**4`, up to 500 parcels. Each parcel at most once.
- Empty lists, or a capacity of 0, give 0.
- Do not change the lists you are given.

## Think about

In the 2-D version, "take parcel `i`" reads row `i - 1`. In one array, how can you make sure the cell you read is still the row `i - 1` value?
