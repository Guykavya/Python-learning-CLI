# Parse a date with helpful errors

Write `parse_date(text)` that turns `"YYYY-MM-DD"` into a tuple of three ints
`(year, month, day)`. Surrounding spaces are allowed. Every failure raises `ValueError` with a
message that says what to type. Check in this order:

1. **Shape**: after `strip()`, splitting on `"-"` must give exactly 3 parts, of lengths 4, 2
   and 2. Otherwise:
   `date must look like YYYY-MM-DD, for example 2025-03-14, got <text!r>`
2. **Digits**: converting each part with `int()` must work. Otherwise:
   `date must use digits only, like 2025-03-14, got <text!r>`.
   Raise this one **`from None`**: the `int()` error inside adds nothing for the reader.
3. **Month** from 1 to 12: `month must be from 1 to 12, got <month>`
4. **Day** from 1 to the length of that month, with February having 29 days in a leap year
   (divisible by 4, except century years not divisible by 400):
   `day must be from 1 to <last day> for <year>-<month as 2 digits>, got <day>`

`<text!r>` means the **original** text, with `repr`.

**Examples**

```python
parse_date("2025-03-14")      # (2025, 3, 14)
parse_date(" 2024-02-29 ")    # (2024, 2, 29)
parse_date("14/03/2025")      # ValueError: date must look like YYYY-MM-DD, for example 2025-03-14, got '14/03/2025'
parse_date("2025-O3-14")      # ValueError: date must use digits only, like 2025-03-14, got '2025-O3-14'
parse_date("2025-13-01")      # ValueError: month must be from 1 to 12, got 13
parse_date("2023-02-29")      # ValueError: day must be from 1 to 28 for 2023-02, got 29
```
