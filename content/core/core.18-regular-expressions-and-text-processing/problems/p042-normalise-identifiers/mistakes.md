- Using `search` or `match` instead of `fullmatch`: `abcde-1` would match `bcde-1` (search) and
  `ab-12x` would match `ab-12` (match).
- `\w{2,4}` for the prefix: `\w` includes digits, `_` and Unicode letters, so `a1-5` passes.
- `[-_/]*` instead of `[-_/]?`: lets `ab--1` through.
- `\s*` around the separator before stripping: tabs inside the id would then be allowed too.
  The task says spaces.
- Using `int(number)` and `:04d`: drops zeros the user typed in a long number.
- Deduping on the raw line: `po-7` and `PO_0007` are the same id after normalising.
- Using a set for the result: it loses the input order.
