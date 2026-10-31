## Approach

Read the profile top-down by **tottime** to find where work is actually done, and use
**cumtime** to see which caller that work belongs to. The model answer is in `answer.md`.

## Key points

- `tottime` = own time; `cumtime` = own time + everything called. Entry points like `main` and
  `exec` always have a cumtime close to the whole run and are almost never the thing to fix.
- `percall` is rounded to 3 decimals, so `0.000` only means "less than half a millisecond". Divide
  `tottime` by `ncalls` yourself.
- A function called very often with a small per-call cost (`find_user`, 3.9 µs × 100,000) is the
  classic hot spot. The fix is to call it less, or make each call O(1).
- Speed-up limit (Amdahl's law): making a part that is 11% of the run infinitely fast saves at
  most 11%.

## The fix, and measuring it

```python
def build(lines):
    totals = {}
    for line in lines:
        name, value = parse(line)
        totals[name] = totals.get(name, 0) + value
    return totals
```

The `users` list only answered "seen before?", which `totals` already knows. Profile again after
the change: `find_user` disappears and `build`, `parse` and `load` become the top lines.

## Another way

`python -m cProfile -s tottime shop.py` gives the same table without editing the code. Saving
the stats with `-o shop.prof` lets you open them in `pstats` (`print_callers("find_user")`) or a
viewer like snakeviz.
