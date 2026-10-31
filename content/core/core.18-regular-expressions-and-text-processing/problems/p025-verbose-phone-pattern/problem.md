# Verbose patterns: a readable phone number parser

Here is a working pattern for US phone numbers:

```python
r"(?:\+1[ -]?)?(?P<area>\([2-9]\d{2}\)|[2-9]\d{2})[-. ]?(?P<exchange>\d{3})[-. ]?(?P<line>\d{4})(?:\s*(?:ext\.?|x)\s*(?P<ext>\d{1,5}))?"
```

Could you fix a bug in it next month? With `re.VERBOSE`, whitespace in a pattern is ignored
and `#` starts a comment, so the same pattern can be laid out on many lines with a note on each
piece. Your job is to write that readable version and use it.

Write in `solution.py`:

1. `PHONE_RE`, compiled with `re.VERBOSE`, spread over several lines, with `#` comments.
2. `parse_phone(s: str) -> dict | None`.

The rules (North American numbers):

- Optional country code `+1`, followed by an optional space or hyphen.
- **Area code**: three digits, the first one 2–9. Either in brackets `(555)` or bare `555`.
  Unbalanced brackets like `(555` or `555)` are invalid.
- An optional separator: one space, `-` or `.`.
- **Exchange**: three digits.
- An optional separator: one space, `-` or `.`.
- **Line**: four digits.
- Optional **extension**: optional whitespace, then `ext`, `ext.` or `x`, optional whitespace,
  then 1 to 5 digits.
- Spaces at the start and end of `s` are ignored. Nothing else may be in the string.

Return `{"area": ..., "exchange": ..., "line": ..., "ext": ...}` with digit strings (the area
**without** brackets), and `"ext": None` when there is no extension. Return `None` when the
string is not a valid number.

**Example**

```python
parse_phone("(555) 123-4567")
# {'area': '555', 'exchange': '123', 'line': '4567', 'ext': None}
parse_phone("+1 555.123.4567 ext. 89")
# {'area': '555', 'exchange': '123', 'line': '4567', 'ext': '89'}
parse_phone("5551234567")      # {'area': '555', 'exchange': '123', 'line': '4567', 'ext': None}
parse_phone("(155) 123-4567")  # None   (area code cannot start with 1)
parse_phone("(555 123-4567")   # None   (unbalanced bracket)
```

**Two verbose-mode traps:** a space you *mean* must be written as `[ ]` or `\ ` (a bare space
is ignored), and a `#` you mean must be `\#`. Inside `[...]` spaces and `#` are kept as they are.
