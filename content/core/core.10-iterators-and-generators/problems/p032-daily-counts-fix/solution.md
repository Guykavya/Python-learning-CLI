## The bug

`groupby` only groups items that are **next to each other**. When a new key appears, it
starts a new group, even if that key was already seen earlier. With merged logs the date
`2026-10-05` appears in two separate runs, so the loop sees it twice. The line
`counts[day] = len(list(group))` **replaces** the first count with the second, so earlier
logins are lost.

The teammate's test used logs already sorted by date, which is why it passed.

## Fixed code

```python
from itertools import groupby


def day_of(line):
    return line.split()[0]


def count_by_day(lines):
    records = (line.strip() for line in lines)
    records = (line for line in records if line)
    counts = {}
    for day, group in groupby(sorted(records, key=day_of), key=day_of):
        counts[day] = len(list(group))
    return counts
```

`sorted(...)` puts every line of the same day next to each other, so each day forms one group.

## Complexity

O(n log n) because of the sort, and O(n) memory, because `sorted` builds a list of all lines.

## Another way

You do not need `groupby` at all to count. A plain dict works on unsorted data and stays lazy
(the pipeline reads one line at a time):

```python
counts = {}
for line in records:
    day = day_of(line)
    counts[day] = counts.get(day, 0) + 1
```

Rule of thumb: use `groupby` when the data is already sorted (or when you want runs on purpose,
like run-length encoding). To **total** by key, use a dict.
