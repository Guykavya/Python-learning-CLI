## Hint 1

`ws.cell(row, col, value)` guesses the type from the value: a string starting with `=` becomes a formula (`data_type == "f"`). Which attribute of the cell can you set afterwards to force text?

## Hint 2

```text
cell = ws.cell(row, col, value)
if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"): cell.data_type = "s"
return cell
```
