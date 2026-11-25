## Approach

1. The denominator is 6 - 6 = 0: `DIVIDE` returns `BLANK`.
2. There is no product in category Z: the sum over no rows is `BLANK` (not 0).
3. `COALESCE` replaces the blank by `0`.
4. `ISBLANK` is true: the `IF` returns `-1`.
5. `t = 180`, `q = 6`: `DIVIDE(180, 6)` is `30`.

## Code

```text
BLANK
BLANK
0
-1
30
```

## Complexity

Not applicable (a trace problem).

## Another way

Show a zero only where a zero is true: a store that was open and sold nothing has revenue 0, but a month with no data at all should stay blank, or the visual shows a row of zeros for every month of the calendar.
