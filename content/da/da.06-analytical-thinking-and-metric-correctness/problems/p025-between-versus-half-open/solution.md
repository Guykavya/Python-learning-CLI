## Approach

`"2025-02-28"` is `2025-02-28 00:00:00`. The closed `between` therefore stops at the very first instant of the 28th and
loses the rest of that day. The half-open filter ends at the first instant of March.

1. `closed`: Feb 1 in, Feb 14 in, Feb 28 00:00 in (equal to the end), Feb 28 15:30 out, 23:59:59.5 out, Mar 1 out.
2. `half_open`: all of February is in (five timestamps), Mar 1 00:00 is out (the end is excluded).
3. Counts: 3 and 5.
4. The two timestamps only the half-open version keeps are the 28th at 15:30 and at 23:59:59.5 (the seconds are printed
   without the `.5`).
5. `last_day` is the 28th: three timestamps; only one (midnight) survives `closed`.
6. `between("2025-02-01", "2025-03-01")` includes the end, so the first instant of March is counted as February: all six.

## Output

```text
[True, True, True, False, False, False]
[True, True, True, True, True, False]
3 5
['28 15:30:00', '28 23:59:59']
3 1
6
```
