# Project: a lazy log-processing pipeline

A server writes millions of log lines. You must answer questions about them without ever holding
all the lines in memory. You will build the answer as a **pipeline**: small generator stages, each
one reading from the stage before it, one item at a time.

The lines arrive as any iterable of strings (a list in the tests, or a generator that may be very
long or endless). Lines may end with `"\n"`. (Reading real files comes in the Files module; the
code you write here will work on a file object unchanged.)

## The log format

```text
2024-05-01 10:15:40 ERROR db: connection lost
<date>     <time>   <level> <source>: <message>
```

A line is **valid** when all of these hold (after removing whitespace at both ends of the line):

1. `line.split(maxsplit=3)` gives exactly 4 parts: `date`, `time`, `level`, `rest`.
2. `date` looks like `YYYY-MM-DD`: 10 characters, `-` at positions 4 and 7, digits everywhere else.
3. `time` looks like `HH:MM:SS`: 8 characters, `:` at positions 2 and 5, digits everywhere else,
   with hour < 24, minute < 60 and second < 60.
4. `level` is one of `DEBUG`, `INFO`, `WARNING`, `ERROR` (upper case, exactly).
5. `rest` contains `": "`. Split it at the **first** `": "`: the part before is the `source`, the
   part after is the `message`. The source must be non-empty and contain no spaces. The message,
   with spaces removed at both ends, must be non-empty. (The message may contain more `": "`.)

A valid line becomes a **record**, a dict with five string keys:

```python
{"date": "2024-05-01", "time": "10:15:40", "level": "ERROR", "source": "db", "message": "connection lost"}
```

## What to write in `solution.py`

| Function | Kind | What it does |
|---|---|---|
| `parse_line(line)` | normal function | the record dict, or `None` if the line is not valid |
| `parse_lines(lines)` | generator | yields the record of every valid line, **skipping** invalid ones |
| `at_least(records, min_level)` | normal function returning an iterator | records whose level is `min_level` or more serious. Order: `DEBUG < INFO < WARNING < ERROR`. An unknown `min_level` raises `ValueError` **at once**, when `at_least` is called, not later. |
| `count_per_minute(records)` | generator | for each run of records in the same minute, yields `("YYYY-MM-DD HH:MM", count)`. Records arrive in time order, so use `itertools.groupby`. Minutes with no records are not yielded. |
| `summarize(records)` | normal function | one pass, returns a dict (see below) |
| `first_messages(lines, min_level, n)` | normal function | a list of the first `n` messages at `min_level` or above, each as `"source: message"`. It reads only as many lines as it needs. |

`summarize(records)` returns:

```python
{
    "total": 6,                                   # number of records
    "by_level": {"INFO": 2, "DEBUG": 1, ...},     # only levels that appear
    "top_source": "db",                           # source with most records; tie -> alphabetically first; None if no records
    "first": "2024-05-01 10:15:02",               # "date time" of the first record; None if no records
    "last": "2024-05-01 10:18:00",                # "date time" of the last record; None if no records
}
```

It must make **one pass** over `records` (they may be a generator) and must not store the records.

## Laziness rules (the tests check them)

- Creating any of the generators reads **nothing** from the input.
- Every stage reads from its input only when its own caller asks for the next item.
- `first_messages(lines, "ERROR", 2)` stops reading lines right after the second error line.
- Everything works on an endless stream of lines when the caller takes a limited number of items.

## Example

```python
lines = [
    "2024-05-01 10:15:02 INFO web: started\n",
    "2024-05-01 10:15:09 DEBUG db: pool size 5\n",
    "garbage line\n",
    "2024-05-01 10:15:40 ERROR db: connection lost\n",
    "\n",
    "2024-05-01 10:16:01 WARNING web: slow request /home\n",
    "2024-05-01 10:16:30 ERROR web: timeout: upstream\n",
    "2024-05-01 10:16:31 CRITICAL db: unknown level\n",
    "2024-05-01 10:18:00 INFO db: recovered\n",
]

len(list(parse_lines(lines)))                       # 6  (3 lines are invalid)
list(count_per_minute(parse_lines(lines)))
# [("2024-05-01 10:15", 3), ("2024-05-01 10:16", 2), ("2024-05-01 10:18", 1)]
[r["message"] for r in at_least(parse_lines(lines), "WARNING")]
# ["connection lost", "slow request /home", "timeout: upstream"]
first_messages(lines, "ERROR", 2)
# ["db: connection lost", "web: timeout: upstream"]
summarize(parse_lines(lines))["top_source"]         # "db"   (db and web have 3 each; "db" < "web")
```

Plan your stages before you write code, and test each stage alone first (for example in the
playground). Keep each function short.
