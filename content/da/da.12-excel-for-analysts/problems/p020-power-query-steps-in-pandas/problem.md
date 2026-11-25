# Power Query steps in pandas

Chapters 9.3 and 9.4. A Power Query is a list of **steps** applied one after the other: trim the text, fix the types, drop the bad rows, reshape, summarise. Power Query cannot run offline; this problem checks the numbers and the steps in pandas, not the Power Query objects.

Write `apply_steps(df, steps)`. `steps` is a list of dicts; each has a `"step"` name. Apply them **in order** to a **copy** of `df` (never change the input) and return the result with a reset index. The steps:

| `"step"` | other keys | what it does |
|---|---|---|
| `trim` | `columns` | strip spaces at both ends of the text in those columns |
| `lower`, `upper`, `proper` | `columns` | text case (`proper` = `str.title`) |
| `replace` | `column`, `old`, `new` | `str.replace(old, new)` (plain text, not a pattern) |
| `change_type` | `types`: `{column: "int" \| "float" \| "date"}` | numbers with `pd.to_numeric(errors="coerce")` (a bad value becomes `NaN`; `"int"` keeps `NaN` as a float column and otherwise an integer column), dates with `pd.to_datetime(format="%Y-%m-%d", errors="coerce")` |
| `filter_blanks` | `column` | drop the rows where the column is `NaN`/`NaT`/`None` or an empty string |
| `unpivot` | `id_columns`, `var_name`, `value_name` | `melt` the other columns |
| `group` | `by`, `aggregations`: `{new_name: (column, "sum" \| "mean" \| "count")}` | group and aggregate |

Any other step name: raise `ValueError("unknown step: <name>")`.

## Example

On the text table `region = [" north "]`, the steps `trim` and `proper` on `region` give `["North"]`.
