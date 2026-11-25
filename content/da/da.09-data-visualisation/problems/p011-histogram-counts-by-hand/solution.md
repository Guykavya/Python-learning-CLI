## Approach

Bins include the left edge and exclude the right edge, except the last bin, which includes both.

- `[0, 10)`: 3, 7 -> 2
- `[10, 20)`: 10, 12, 18 -> 3
- `[20, 30)`: 20, 20, 25, 29 -> 4
- `[30, 40]`: 30, 35, 40 -> 3

All 12 values are counted. A single value 20 goes to the third bin, a single 40 to the fourth (the last bin is closed on the right), a single 10 to the second.

## Code

```text
[2, 3, 4, 3]
12
[0, 0, 1, 0]
[0, 0, 0, 1]
[0, 1, 0, 0]
```

## Complexity

Not applicable (a trace problem).

## Another way

`np.histogram(values, bins)` gives the same counts without drawing; use it when you only need the numbers.
