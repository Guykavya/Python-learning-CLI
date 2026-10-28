- Putting `if self.style == "markdown": ... elif ...` inside `render`. Every new format then means
  editing `Report`; the formatter objects exist to avoid that.
- `def __init__(self, ..., formatter=PlainFormatter())`. The default object is made once and
  shared by every report.
- In `render(formatter)`, writing `self.formatter = formatter`. The one-time formatter then
  replaces the stored one for every later call.
- `isinstance(f, (PlainFormatter, MarkdownFormatter, CsvFormatter))` checks. A perfectly good new
  formatter is then rejected.
- Computing column widths from the rows only. A long header like `quantity` would stick out.
- Forgetting `.rstrip()` on plain lines. The last column is padded too, leaving trailing spaces.
- Storing `rows` as the caller's list. Appending to that list later silently changes the report.
