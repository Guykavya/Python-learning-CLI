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
