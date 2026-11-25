## Approach

- `len(orders) = 3`, `len(lines) = 6`, and the merge keeps one row per line: `len(flat) = 6`.
- The true freight is 10 + 20 + 30 = `60.0`.
- In the flat table: 3 x 10 + 2 x 20 + 1 x 30 = `100.0`.
- The ratio is 100 / 60 = `1.67`.

## Code

```text
3 6 6
60.0
100.0
1.67
```

## Complexity

Not applicable (a trace problem).

## Another way

Keep the freight in an **orders** fact table (one row per order) related to the same dimensions; a measure `SUM(Orders[Freight])` then gives 60 at every level.
