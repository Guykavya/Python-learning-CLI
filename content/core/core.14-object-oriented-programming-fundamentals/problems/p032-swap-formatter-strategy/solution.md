## Approach

This is the **strategy** pattern, a classic use of composition (chapter section 14). The report
*has* a formatter. The formatter is a small object with one job, and `render` delegates to it:
`self.formatter.format(...)`. Swapping the formatter changes the output without touching the
report.

Compare with inheritance: `PlainReport`, `MarkdownReport`, `CsvReport` as subclasses. Then a report
cannot change its format after it is created, and adding "Markdown with a total line" means yet
another subclass. With composition you just pass another object.

The formatters share no base class. `render` only needs an object with a `format` method: duck
typing (section 15). The test's `CountFormatter` proves it.

`formatter=None` plus "create inside `__init__`" gives each report its own default formatter.
(A default like `formatter=PlainFormatter()` would be built once, when `def` runs, and shared.)

## Code

```python
class PlainFormatter:
    def format(self, title, headers, rows):
        table = [[str(v) for v in headers]] + [[str(v) for v in row] for row in rows]
        widths = [max(len(line[i]) for line in table) for i in range(len(headers))]
        lines = [title, "=" * len(title)]
        for line in table:
            cells = [cell.ljust(width) for cell, width in zip(line, widths)]
            lines.append("  ".join(cells).rstrip())
        return "\n".join(lines)


class MarkdownFormatter:
    def format(self, title, headers, rows):
        def table_line(values):
            return "| " + " | ".join(str(v) for v in values) + " |"

        lines = [f"## {title}", "", table_line(headers), table_line(["---"] * len(headers))]
        lines += [table_line(row) for row in rows]
        return "\n".join(lines)


class CsvFormatter:
    def __init__(self, sep=","):
        self.sep = sep

    def format(self, title, headers, rows):
        lines = [self.sep.join(str(v) for v in headers)]
        lines += [self.sep.join(str(v) for v in row) for row in rows]
        return "\n".join(lines)


class Report:
    def __init__(self, title, headers, rows, formatter=None):
        self.title = title
        self.headers = list(headers)
        self.rows = []
        for row in rows:
            self.add_row(*row)
        self.formatter = PlainFormatter() if formatter is None else formatter

    def add_row(self, *values):
        if len(values) != len(self.headers):
            raise ValueError(f"expected {len(self.headers)} values, got {len(values)}")
        self.rows.append(tuple(values))

    def render(self, formatter=None):
        f = self.formatter if formatter is None else formatter
        return f.format(self.title, self.headers, self.rows)
```

`__init__` reuses `add_row`, so the length check exists once. `tuple(values)` makes a copy, so the
caller's lists cannot reach inside the report.

## Complexity

`render` is O(total number of cells) for every formatter. `add_row` is O(k) for k values.

## Another way

Since a strategy here has only one method, a plain **function** works too:
`report.formatter = markdown` where `def markdown(title, headers, rows): ...`, and `render` calls
`self.formatter(title, headers, rows)`. Classes are better once a strategy has settings (like
`sep`) or several methods; for one setting, a closure or `functools.partial` also works.
