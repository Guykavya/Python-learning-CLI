## Walkthrough

- Each call of `make_pair` creates its own cell for `n`; `get1`/`inc1` share one, `get2`/`inc2`
  the other. `inc1` runs twice and `inc2` once, so `2 1`.
- `show` reads the cell for `value` when called. By then `value` is `"late"`.
- All three lambdas in `loop_funcs` read the single cell for `i`, which holds 2 after the loop:
  `[4, 4, 4]`. In `fixed_funcs` each lambda captured `i` as a default when it was created:
  `[0, 1, 4]`.
- `get1` has one free variable, `n`, whose cell holds 2. `get1` and `inc1` share that very cell,
  so `is` gives `True`.

## The exact output

```text
2 1
late
[4, 4, 4]
[0, 1, 4]
1 2
True
```
