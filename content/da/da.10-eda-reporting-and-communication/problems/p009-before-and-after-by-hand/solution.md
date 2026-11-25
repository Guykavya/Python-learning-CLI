## Approach

The first four Mondays are before 2 September; the week of 2 September and the three after it form "after".

- before mean = (1.0 + 1.2 + 0.8 + 1.0) / 4 = 1.00
- after mean = (2.6 + 2.4 + 1.6 + 2.0) / 4 = 2.15
- change = +1.15
- `wrong` uses `>`, drops the week of 2 September (the highest value, 2.6) and keeps 3 weeks: (2.4 + 1.6 + 2.0) / 3 = 2.00

## Code

```text
4 4
1.00 2.15
+1.15
3 2.00
```

## Complexity

Not applicable (a trace problem).

## Another way

`pd.cut` with explicit bins and `right=False` makes the boundary rule visible in one place, instead of in a `<` and a `>=` that can drift apart.
