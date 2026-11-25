# What does `csv` really read?

Chapter section 7.2. `csv.reader` takes any iterable of lines. It splits on commas **outside** quotes, turns a doubled quote `""` inside a quoted field into one `"`, keeps spaces as they are, and does not complain about rows of different lengths.

```python
import csv

lines = [
    "name,city,score",
    'Asha,"Pune, MH",90',
    'Ben,"say ""hi""",85',
    "Chen ,Delhi, 70",
    "",
    "Dev,Goa",
]

for number, row in enumerate(csv.reader(lines), start=1):
    print(number, len(row), row)
```

Hand-trace the program and write **every printed line** in `answer.txt`. Each line is `number`, a space, `len(row)`, a space, then the list exactly as Python prints it (`repr` of the strings, so quotes matter: `'Pune, MH'` is printed with single quotes unless the text contains a single quote).

Think about each of these before you answer: the quoted comma, the doubled quote, the trailing space after `Chen`, the space before `70`, the empty line, and the short row.

## Answer format

Six lines, one per input line, in order.

## After you answer

- Which line would break a program that does `row[2]`? Which line would silently make `score` text with a space?
- What would you add to a loader to *report* these rows instead of crashing?
