## Approach

- `">=10"`: only the number 12 (8 is too small, text never matches) -> 1.
- `"<>North"`: all 8 cells except `North` and `north` -> 6.
- `"N*"`: North, north, Nord, N/A -> 4.
- `"north"`: North and north -> 2.
- `"<>"`: every non-empty cell: 8 - 1 = 7.
- `"="`: the one empty cell -> 1.

## Code

```text
1
6
4
2
7
1
```

## Complexity

Not applicable (a trace problem).

## Another way

Put the same six formulas in a spare column of a real sheet: the habit of testing a criterion on a small column before using it on 3,000 rows saves a lot of "why is my SUMIFS too small" time.
