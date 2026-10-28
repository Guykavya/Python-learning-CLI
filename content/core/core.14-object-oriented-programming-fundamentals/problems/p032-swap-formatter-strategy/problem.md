# Swap the report formatter

A report can be shown as plain text, as Markdown, or as CSV. The data is the same; only the way it
is written changes. Instead of three report classes, the report **holds a formatter object** and
asks it to do the writing. You can swap the formatter at any time. Write it in `solution.py`.

**`Report(title, headers, rows, formatter=None)`**

- `headers` is a list of column names; `rows` is a list of rows (each a list or tuple of values).
- Store `title`, `headers` (as a list) and `rows` (as a **new** list of tuples, so later changes to
  the caller's list do not affect the report).
- Every row must have exactly `len(headers)` values, otherwise `ValueError`.
- `formatter` defaults to a new `PlainFormatter()`. Store it in the attribute `formatter`; code may
  replace it later (`report.formatter = MarkdownFormatter()`).
- `add_row(*values)` adds one row (same length check).
- `render(formatter=None)` returns `f.format(title, headers, rows)`, where `f` is the given
  formatter, or `self.formatter` if none is given. A formatter given to `render` is used only for
  that call; it does not replace `self.formatter`.

Any object with a method `format(title, headers, rows)` that returns a string can be a formatter.
Write three. All values are turned into text with `str()`. Lines are joined with `"\n"`, with no
newline at the end.

- **`PlainFormatter`**: the title, a line of `=` as long as the title, the header line, then one line
  per row. Each column is padded with `ljust` to the width of its widest cell (header included),
  columns are separated by two spaces, and spaces at the end of each line are removed.
- **`MarkdownFormatter`**: `## title`, an empty line, then a Markdown table:
  `| item | qty |`, then `| --- | --- |` (one `---` per column), then one `| ... |` line per row.
- **`CsvFormatter(sep=",")`**: no title. The header line and the rows, values joined with `sep`.

**Example**

```python
r = Report("Sales", ["item", "qty"], [("pen", 3), ("notebook", 12)])
print(r.render())
# Sales
# =====
# item      qty
# pen       3
# notebook  12
r.formatter = MarkdownFormatter()
print(r.render())
# ## Sales
#
# | item | qty |
# | --- | --- |
# | pen | 3 |
# | notebook | 12 |
r.render(CsvFormatter(sep=";"))    # 'item;qty\npen;3\nnotebook;12'
r.add_row("ink")                   # ValueError: expected 2 values, got 1
```
