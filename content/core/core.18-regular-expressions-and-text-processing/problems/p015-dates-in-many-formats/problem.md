# Dates in many formats

Notes, e-mails and spreadsheets mix date styles: `05/03/2024` here, `2024-03-05` there.
Before you can sort or compare them, you have to find them all and **normalise** them to one
format. ISO format `yyyy-mm-dd` is the best choice, because ISO strings sort correctly as plain text.

Write `find_dates(text: str) -> list[str]` in `solution.py`.

Find every date in one of these two forms:

1. **Indian style** `d/m/yyyy`: day, slash, month, slash, year. Day and month have **1 or 2**
   digits, the year exactly 4. Day comes first: `05/03/2024` is 5 March 2024.
2. **ISO style** `yyyy-mm-dd`: exactly 4, 2 and 2 digits with hyphens.

Rules:

- A date must not be glued to other letters, digits or underscores: `x12/05/2024`,
  `12/05/20245` and `2024-03-055` are not dates. Punctuation or spaces around it are fine.
- Check the numbers: month `1`–`12`, day `1`–`31`. Skip dates outside these ranges.
  (No need to check days per month: `31/02/2024` counts.)
- Return each date as `yyyy-mm-dd` with two-digit month and day, in the order they appear
  in the text. A date that appears twice is returned twice.
- Only ASCII digits `0`–`9`.

**Example**

```python
find_dates("Paid on 5/3/2024, due 2024-04-01. Not a date: 13/13/2024")
# ['2024-03-05', '2024-04-01']

find_dates("31/12/2023 then 1/1/2024")
# ['2023-12-31', '2024-01-01']
```
