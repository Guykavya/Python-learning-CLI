# Strategy as a function

`starter.py` computes a basket total and applies a discount chosen **by name**. Every new
discount means editing `checkout` (and a typo in the name is only caught at run time). That
breaks the open/closed principle.

The **strategy pattern** says: pass the varying step in. In Python the strategy is simply a
**function**. Here a strategy takes the total and returns the discounted total.

Copy `starter.py` to `solution.py` and write:

- `no_discount(total)`: returns the total unchanged.
- `percent_off(p)`: returns a **strategy** that takes off `p` percent (`percent_off(10)(200)` is `180`).
- `flat_off(n)`: returns a strategy that takes off `n` but never goes below `0`.
- `checkout(items, strategy=no_discount)`: sums `items`, calls `strategy(total)` **once**, and
  returns the result rounded to 2 decimals.

`checkout` must not contain any `if` or any string comparison: it just calls the function it was given.

**Example**

```python
checkout([100, 100])                       # 200
checkout([100, 100], percent_off(10))      # 180.0
checkout([30, 20], flat_off(5))            # 45
checkout([10, 10], lambda total: total / 2)   # 10.0, any callable works
```

Because a strategy is any callable, callers can also use a `lambda` or `functools.partial`,
which the tests try.
