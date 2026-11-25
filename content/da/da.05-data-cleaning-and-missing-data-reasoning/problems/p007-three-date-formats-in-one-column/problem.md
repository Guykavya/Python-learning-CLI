# Three date formats in one column

Chapter section 3.4. The `signup` column holds `"2024-03-05"`, `"05/03/2024"` and `"Mar 05, 2024"`. A single
`pd.to_datetime(..., dayfirst=...)` call gets one of the formats wrong **without any warning**: the slash date
`05/03/2024` is 5 March in this survey (day first), but a parser that guesses month first reads 3 May. The safe method
is to look at the **pattern** of each value, pick the format that belongs to it, and parse with that exact format.

Write `parse_signup(s)`. `s` is a Series of text (values may be missing). Return a tuple `(dates, bad)`:

- `dates` is a datetime Series with the **same index** as `s`.
- For each value: strip spaces, then match the **whole** text against one of three patterns:

| pattern | example | meaning |
|---|---|---|
| 4 digits, `-`, 2 digits, `-`, 2 digits | `2024-03-05` | year-month-day |
| 2 digits, `/`, 2 digits, `/`, 4 digits | `05/03/2024` | **day**/month/year |
| 3 letters (first capital), a space, 2 digits, `,`, a space, 4 digits | `Mar 05, 2024` | month name, day, year |

- A text that matches a pattern but is **not a real date** (`31/04/2024`, `2024-02-30`) becomes `NaT`. A text that
  matches **no** pattern (`March 5`) becomes `NaT`. A missing input stays `NaT`.
- `bad` is the **sorted list of distinct stripped texts** that were present but could not be read (the two cases above).
  Missing inputs are not listed. When everything was read, `bad` is `[]`.

Do not change `s`. Do not use `dayfirst=True` or `format="mixed"`: both guess.

## Example

```python
import pandas as pd

s = pd.Series(["2024-03-05", "05/03/2024", "Mar 05, 2024", "31/04/2024", "2024-02-30", None, "March 5", "13/01/2024"])
dates, bad = parse_signup(s)
print([None if pd.isna(d) else d.strftime("%Y-%m-%d") for d in dates])
print(bad)
```

```text
['2024-03-05', '2024-03-05', '2024-03-05', None, None, None, None, '2024-01-13']
['2024-02-30', '31/04/2024', 'March 5']
```

All three spellings of 5 March give the same date, `13/01/2024` is 13 January, and `bad` is sorted as text.
