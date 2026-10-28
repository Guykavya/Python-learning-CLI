import pytest

from solution import CsvFormatter, MarkdownFormatter, PlainFormatter, Report

ROWS = [("pen", 3), ("notebook", 12)]

PLAIN = "Sales\n=====\nitem      qty\npen       3\nnotebook  12"
MARKDOWN = "## Sales\n\n| item | qty |\n| --- | --- |\n| pen | 3 |\n| notebook | 12 |"


def make():
    return Report("Sales", ["item", "qty"], ROWS)


def test_report_stores_data():
    r = make()
    assert r.title == "Sales" and r.headers == ["item", "qty"], "Store title and headers."
    assert r.rows == [("pen", 3), ("notebook", 12)], "Store rows as a list of tuples."
    assert isinstance(r.formatter, PlainFormatter), "The default formatter is a PlainFormatter object."


def test_rows_are_copied():
    rows = [["pen", 3]]
    r = Report("T", ["a", "b"], rows)
    rows.append(["ink", 1])
    rows[0][1] = 99
    assert r.rows == [("pen", 3)], "Keep your own list of tuples so changes to the caller's list do not reach the report."


def test_default_formatters_not_shared():
    a = make()
    b = make()
    assert a.formatter is not b.formatter, (
        "Each report should get its own PlainFormatter. Use formatter=None and create it inside __init__."
    )


def test_plain_render():
    assert make().render() == PLAIN, (
        "Plain: title, '=' line, then columns padded to the widest cell with ljust, 2 spaces between, no trailing spaces."
    )


def test_plain_width_uses_header_too():
    out = PlainFormatter().format("T", ["quantity", "x"], [(1, "a")])
    assert out == "T\n=\nquantity  x\n1         a", "A column is as wide as its widest cell, and the header counts."


def test_markdown_render_after_swap():
    r = make()
    r.formatter = MarkdownFormatter()
    assert r.render() == MARKDOWN, "Markdown: '## title', empty line, header line, '| --- |' line, row lines."


def test_csv_formatter():
    assert make().render(CsvFormatter()) == "item,qty\npen,3\nnotebook,12", "CSV has no title; values joined with sep."
    assert make().render(CsvFormatter(sep=";")) == "item;qty\npen;3\nnotebook;12", "Use the sep given to CsvFormatter."


def test_render_argument_is_one_time():
    r = make()
    r.render(MarkdownFormatter())
    assert isinstance(r.formatter, PlainFormatter), "render(f) uses f only for that call; self.formatter stays the same."
    assert r.render() == PLAIN, "After a one-time formatter, render() uses the stored formatter again."


def test_constructor_formatter_argument():
    r = Report("Sales", ["item", "qty"], ROWS, formatter=MarkdownFormatter())
    assert r.render() == MARKDOWN, "A formatter passed to Report(...) becomes self.formatter."


def test_any_object_with_format_works():
    class CountFormatter:
        def format(self, title, headers, rows):
            return f"{title}: {len(rows)} rows"

    r = make()
    r.formatter = CountFormatter()
    assert r.render() == "Sales: 2 rows", (
        "render must only call self.formatter.format(title, headers, rows). Do not check the formatter's type."
    )


def test_add_row():
    r = make()
    r.add_row("ink", 1)
    assert r.rows[-1] == ("ink", 1), "add_row(*values) adds one tuple at the end."
    assert r.render(CsvFormatter()).endswith("\nink,1"), "The new row appears in the output."


def test_wrong_row_length():
    with pytest.raises(ValueError):
        Report("T", ["a", "b"], [(1, 2), (3,)])
    r = make()
    with pytest.raises(ValueError):
        r.add_row("ink")
    with pytest.raises(ValueError):
        r.add_row("ink", 1, 2)
    assert len(r.rows) == 2, "A rejected row must not be added."


def test_empty_rows():
    r = Report("Empty", ["a"], [])
    assert r.render() == "Empty\n=====\na", "With no rows, plain shows the title, its line and the header."
    assert r.render(MarkdownFormatter()) == "## Empty\n\n| a |\n| --- |", "Markdown with no rows has only the header lines."
