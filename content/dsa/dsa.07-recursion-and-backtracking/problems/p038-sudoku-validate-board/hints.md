## Hint 1

For each unit, collect the filled digits. The unit is fine if there are no repeats: `len(digits) == len(set(digits))`.

## Hint 2

One pass: keep `rows = [set() for _ in range(9)]`, the same for `cols` and `boxes`. For each filled cell `(r, c)` with digit `d`, if `d` is already in `rows[r]`, `cols[c]` or `boxes[b]`, return `False`; otherwise add it to all three.

## Hint 3

```
b = (r // 3) * 3 + c // 3
if d in rows[r] or d in cols[c] or d in boxes[b]: return False
rows[r].add(d); cols[c].add(d); boxes[b].add(d)
```
