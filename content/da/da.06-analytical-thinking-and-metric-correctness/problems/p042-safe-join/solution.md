## Approach

Two independent checks, as in the chapter. `validate="m:1"` makes pandas refuse a join whose right side is not unique, so
the usual fan-out never happens. The row-count check is a second net for the cases where you declared a relationship that
allows growth (`"1:m"`) but expected none, or where a key problem changes the count. It only makes sense for a **left**
join: an inner join drops rows by design.

## Code

```python
def safe_join(left, right, on, how="left", validate="m:1", label=""):
    out = left.merge(right, on=on, how=how, validate=validate)
    if how == "left" and len(out) != len(left):
        name = label or f"join on {on}"
        raise AssertionError(f"{name}: rows changed {len(left)} -> {len(out)} (fan-out or a lost key?)")
    return out
```

## Complexity

The merge dominates: O(n + m) with a hash join. The checks are O(1) (`len`) plus a uniqueness test inside `validate`.

## Another way

Raise `ValueError` instead of `AssertionError` (asserts can be switched off with `python -O`; a real `raise` cannot).
The chapter uses `AssertionError` to match the style of its tests. A wrapper that also logs the row counts (like the
change log of da.05) turns every join into an audit line.
