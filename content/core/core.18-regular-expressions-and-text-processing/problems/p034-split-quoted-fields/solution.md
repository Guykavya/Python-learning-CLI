## Approach

Write a pattern for **one field including the comma before it**:

- `(?:^|,)` the field starts at the start of the line or just after a comma. This is what makes
  `a,,b` give three fields and stops `finditer` from inventing an extra empty field at the end.
- `\s*` spaces before the value are skipped.
- Then either a quoted value `"(?P<quoted>(?:[^"]|"")*)"` (anything but a quote, or a doubled
  quote) or a plain value `(?P<plain>[^,"]*?)`. The plain value is **lazy**, so trailing spaces are
  left for the next `\s*` instead of being captured.
- `\s*(?=,|$)` spaces after it, then a lookahead: the field must end before a comma or the end.
  The comma is not consumed; it starts the next field.

For each match, the group that took part tells which alternative matched. `None` means "this
group did not participate", so test with `is not None` (an empty quoted field is `""`, which is
falsy but present).

## Code

```python
import re

FIELD = re.compile(
    r"""
    (?: ^ | , )
    \s*
    (?:
        "(?P<quoted>(?:[^"]|"")*)"
      | (?P<plain>[^,"]*?)
    )
    \s*
    (?= , | $ )
    """,
    re.VERBOSE,
)


def split_fields(line: str) -> list[str]:
    fields = []
    for m in FIELD.finditer(line):
        if m.group("quoted") is not None:
            fields.append(m.group("quoted").replace('""', '"'))
        else:
            fields.append(m.group("plain"))
    return fields
```

## Complexity

O(n) for a line of length n: each character is consumed once by one field (the lazy `*?` grows one
character at a time while checking the lookahead, which stays cheap because `[^,"]` stops at
every comma).

## Another way

The standard library does this for real: `next(csv.reader([line], skipinitialspace=True))`. A
hand-written loop with a "inside quotes?" flag also works and is a good exercise in state.
