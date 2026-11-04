## Walkthrough

| side | range read (with the boundaries at that moment) | values | boundaries after: t b l r |
|---|---|---|---|
| start | | | 0 2 0 3 |
| top | row 0, columns 0..3 | [1, 2, 3, 4] | 1 2 0 3 |
| right | column 3, rows 1..2 | [8, 12] | 1 2 0 2 |
| bottom (1 <= 2) | row 2, columns 2 down to 0 | [11, 10, 9] | 1 1 0 2 |
| left (0 <= 2) | column 0, rows 1 down to 1 | [5] | 1 1 1 2 |
| top | row 1, columns 1..2 | [6, 7] | 2 1 1 2 |
| right | column 2, rows 2..1: `range(2, 2)` is empty | [] | 2 1 1 1 |
| bottom | `top <= bottom` is `2 <= 1`: false, skipped, no line | | |
| left (1 <= 1) | column 1, rows 1 down to 2: `range(1, 1, -1)` is empty | [] | 2 1 2 1 |

Now `top <= bottom` is false and the loop ends.

## Output

```
start 0 2 0 3
top [1, 2, 3, 4] -> 1 2 0 3
right [8, 12] -> 1 2 0 2
bottom [11, 10, 9] -> 1 1 0 2
left [5] -> 1 1 1 2
top [6, 7] -> 2 1 1 2
right [] -> 2 1 1 1
left [] -> 2 1 2 1
[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
```

## Key ideas

- Each side uses the boundaries **as already shrunk** by the sides before it. That is why corners are never taken twice:
  `4` is taken by the top side, and the right side starts one row lower.
- The `if top <= bottom` check stops the last row `6 7` from being walked again backwards. Without it, the bottom side
  would read row `bottom = 1` from column 1 down to 1 and add `6` a second time.
- An empty `range` is harmless: the right and left sides of the second lap print `[]` and add nothing. Twelve values,
  each once.
