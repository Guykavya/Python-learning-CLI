# Load one column, and say what was dropped

Chapter section 7.5: nothing may be dropped silently. Write `load_column(path, column, low=None, high=None, dedupe_on=None)` that reads one numeric column of a CSV file and returns `(values, report)`.

- Open the file with `encoding="utf-8"` and `newline=""`; read it with `csv.DictReader`.
- If `column` (or a name in `dedupe_on`) is not in the header: `KeyError` with that name.
- `dedupe_on` is a list of column names. A row whose values in those columns (as raw text) were already seen is a **duplicate**: count it and skip it. Do this check **first**, before parsing.
- Parse the cell with the rules of p009 (strip, lower-case; missing markers `""`, `na`, `n/a`, `nan`, `null`, `none`, `-`, `?`; remove `rs.`, `rs`, `ms`, `%`, `$`, commas, spaces; `float`; not finite is bad). Missing cells are counted under `"missing"`; text that cannot be parsed under `"unparseable"`.
- If `low` is given and the value is below it, or `high` is given and the value is above it, count it under `"out_of_range"` and skip it.
- `values` holds the kept floats in file order. `report` is a dict that **always** has the four keys `"missing"`, `"unparseable"`, `"out_of_range"`, `"duplicate"`.

## Example

```text
id,ms
1,120.5
2, 98ms
2, 98ms
3,N/A
4,abc
5,-5
```

`load_column(path, "ms", low=0, dedupe_on=["id"])` returns
`([120.5, 98.0], {"missing": 1, "unparseable": 1, "out_of_range": 1, "duplicate": 1})`.
