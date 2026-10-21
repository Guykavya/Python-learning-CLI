# Shape areas from commands

Read lines until `done`. Each line describes a shape (numbers may have decimals):

| Line | Area |
|---|---|
| `circle R` | pi x R x R (use `math.pi`) |
| `rect W H` | W x H |
| `square S` | S x S |
| `triangle B H` | B x H / 2 |

For each valid shape print `<shape> area: <area with 2 decimals>`, for example
`rect area: 12.00`.

- Right shape, wrong number of values: print the usage, for example `Usage: rect W H`
  (`Usage: circle R`, `Usage: square S`, `Usage: triangle B H`).
- Any value 0 or less: print `Sizes must be positive`.
- Blank lines are ignored. Any other first word: `Unknown shape: <word>`.

You may assume every value given is a valid number. At the end print `Shapes: N` and
`Total area: <sum with 2 decimals>` counting only the valid shapes.

Use `match` with sequence patterns.
