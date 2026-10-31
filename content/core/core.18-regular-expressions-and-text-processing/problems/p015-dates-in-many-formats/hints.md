## Hint 1

Write the two forms as two separate patterns first and test each with `re.findall`: one for `d/m/yyyy` (what quantifier gives "1 or 2 digits"?) and one for `yyyy-mm-dd`. Put groups around the numbers you need. How do you stop `12/05/20245` from matching?

## Hint 2

To keep text order, both forms must be found in **one** left-to-right scan. Join them with `|` inside one group and put `\b` around the whole thing. With `re.finditer` you get Match objects; a group from the alternative that did not match is `None`. That tells you which form you found.

## Hint 3

```
DATE = \b(?: (d{1,2})/(d{1,2})/(d{4}) | (d{4})-(d{2})-(d{2}) )\b     # d = [0-9]

for m in finditer(DATE, text):
    if m.group(1) is not None: day, month, year = groups 1, 2, 3
    else:                      year, month, day = groups 4, 5, 6
    if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
        append f"{year}-{int(month):02d}-{int(day):02d}"
```
