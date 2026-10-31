## Hint 1

What changes between the three outputs, and what stays the same? The report's data stays the
same. So the report should not contain any formatting code at all. It keeps a formatter object in
`self.formatter` and calls one method on it. What must `render` know about the formatter? Only
that it has a `format(title, headers, rows)` method.

## Hint 2

For the plain table, first turn every cell into text and put the header row on top:
`table = [headers] + rows` (as strings). The width of column `i` is
`max(len(line[i]) for line in table)`. `zip(line, widths)` pairs each cell with its width.

## Hint 3

```
Report.__init__(title, headers, rows, formatter=None):
    store title, list(headers), self.rows = []
    for row in rows: self.add_row(*row)        # one place for the length check
    self.formatter = PlainFormatter() if formatter is None else formatter

render(formatter=None):
    f = self.formatter if formatter is None else formatter
    return f.format(self.title, self.headers, self.rows)

PlainFormatter.format:
    lines = [title, "=" * len(title)]
    for each line of the table: "  ".join(cell.ljust(width) ...).rstrip()
```
