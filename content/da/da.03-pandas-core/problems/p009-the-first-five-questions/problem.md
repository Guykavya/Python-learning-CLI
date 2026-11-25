# The first five questions

Chapter section 5. Before any analysis, ask five questions of a new table: how many rows, how many columns, what type is
each column, how much is missing in each, and are there repeated rows?

Write `first_look(df)` returning a dict with exactly these keys:

| key | value |
|---|---|
| `rows` | number of rows (int) |
| `cols` | number of columns (int) |
| `dtypes` | `{column: dtype as a string}` (for example `"int64"`, `"str"`) |
| `missing` | `{column: number of missing values}` (ints, every column listed) |
| `duplicate_rows` | number of rows that repeat an earlier row (int) |

The input frame is not changed.

## Example

```python
df = pd.DataFrame({"a": [1, 2, 2], "b": ["x", None, None]})
first_look(df)
# {'rows': 3, 'cols': 2, 'dtypes': {'a': 'int64', 'b': 'str'},
#  'missing': {'a': 0, 'b': 2}, 'duplicate_rows': 1}      (pandas 3.1.1)
```
