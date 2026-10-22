# running_totals and running_max with accumulate

Write two functions in `solution.py`, both based on `itertools.accumulate`:

1. `running_totals(numbers)` returns the list of running sums.
2. `running_max(numbers)` returns the list of the biggest value seen so far.

**Examples**

```python
running_totals([1, 2, 3, 4])   # [1, 3, 6, 10]
running_max([3, 1, 4, 1, 5])   # [3, 3, 4, 4, 5]
running_totals([])             # []
```
