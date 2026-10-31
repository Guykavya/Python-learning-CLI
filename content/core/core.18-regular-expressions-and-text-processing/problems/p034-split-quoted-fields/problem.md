# Split a CSV-like line with quoted fields

`line.split(",")` breaks as soon as a field itself contains a comma: in
`"Delhi, India",42` the city is one field, not two. Spreadsheet exports solve this with
quotes. Here you will split such a line with one regex and `finditer`.

(In real programs, use the `csv` module. Writing this by hand teaches you how alternation and
lookahead work together.)

Write `split_fields(line: str) -> list[str]`.

- Fields are separated by commas.
- An **unquoted** field is everything up to the next comma, with spaces around it stripped.
- A **quoted** field is wrapped in double quotes `"..."`. It may contain commas and spaces,
  which are kept exactly. Inside quotes, two double quotes `""` stand for one `"`.
  Spaces **outside** the quotes are ignored.
- Empty fields are kept: `a,,b` has three fields. A line with no commas has one field, even an
  empty line: `""` (empty string) gives `[""]`.
- You may assume the line is well formed (quotes are balanced, and a quoted field is followed only
  by spaces and then a comma or the end).

**Example**

```python
split_fields('"Delhi, India",42')
# ['Delhi, India', '42']

split_fields(' x , y ,')
# ['x', 'y', '']

split_fields('"say ""hi""",2')
# ['say "hi"', '2']
```
