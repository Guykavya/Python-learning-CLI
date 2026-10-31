## Approach

Each stage does one job and passes records on one at a time:

```text
lines -> parse_lines -> at_least -> count_per_minute / summarize / islice
```

- **Parsing** is a normal function `parse_line` that returns `None` for any broken rule. Keeping
  it separate from the loop makes it easy to test, and `parse_lines` just skips the `None`s. Bad
  lines are expected data, not errors, so we do not raise.
- **Filtering** checks its argument first, then returns a generator expression. This split is the
  important trick: a generator function would delay the `ValueError` until the first `next()`,
  maybe far away from the mistake.
- **Grouping** uses `groupby`, which is lazy because logs already arrive in time order. Sorting
  would break laziness and is not needed.
- **Summarising** is a single loop that keeps counters, so it uses memory for the counters only,
  never for the records.
- **first_messages** shows the pay-off: `islice` stops asking after `n` items, so every stage
  before it stops too, and the rest of the input is never read.

## Code

```python
import itertools
from collections.abc import Iterable, Iterator

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]

Record = dict[str, str]


def _is_date(text: str) -> bool:
    if len(text) != 10 or text[4] != "-" or text[7] != "-":
        return False
    return (text[:4] + text[5:7] + text[8:]).isdigit()


def _is_time(text: str) -> bool:
    if len(text) != 8 or text[2] != ":" or text[5] != ":":
        return False
    hh, mm, ss = text[:2], text[3:5], text[6:]
    if not (hh + mm + ss).isdigit():
        return False
    return int(hh) < 24 and int(mm) < 60 and int(ss) < 60


def parse_line(line: str) -> Record | None:
    parts = line.strip().split(maxsplit=3)
    if len(parts) != 4:
        return None
    date, time, level, rest = parts
    if not _is_date(date) or not _is_time(time) or level not in LEVELS:
        return None
    source, sep, message = rest.partition(": ")
    message = message.strip()
    if not sep or not source or " " in source or not message:
        return None
    return {"date": date, "time": time, "level": level, "source": source, "message": message}


def parse_lines(lines: Iterable[str]) -> Iterator[Record]:
    for line in lines:
        record = parse_line(line)
        if record is not None:
            yield record


def at_least(records: Iterable[Record], min_level: str) -> Iterator[Record]:
    if min_level not in LEVELS:
        raise ValueError(f"unknown level {min_level!r}; use one of {LEVELS}")
    lowest = LEVELS.index(min_level)
    return (r for r in records if LEVELS.index(r["level"]) >= lowest)


def _minute(record: Record) -> str:
    return record["date"] + " " + record["time"][:5]


def count_per_minute(records: Iterable[Record]) -> Iterator[tuple[str, int]]:
    for minute, group in itertools.groupby(records, key=_minute):
        yield minute, sum(1 for _ in group)


def summarize(records: Iterable[Record]) -> dict:
    total = 0
    by_level: dict[str, int] = {}
    by_source: dict[str, int] = {}
    first = None
    last = None
    for r in records:
        total += 1
        by_level[r["level"]] = by_level.get(r["level"], 0) + 1
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
        stamp = r["date"] + " " + r["time"]
        if first is None:
            first = stamp
        last = stamp
    top_source = None
    if by_source:
        top_source = min(by_source, key=lambda s: (-by_source[s], s))
    return {"total": total, "by_level": by_level, "top_source": top_source, "first": first, "last": last}


def first_messages(lines: Iterable[str], min_level: str, n: int) -> list[str]:
    wanted = at_least(parse_lines(lines), min_level)
    return [r["source"] + ": " + r["message"] for r in itertools.islice(wanted, n)]
```

## Complexity

Every stage is O(1) work per line. Memory: one line and one record at a time, plus the counters in
`summarize` (one entry per level and per source) and one group in `count_per_minute` (only its
key, because we count the group without storing it). The whole pipeline handles a stream of any
length.

## Another way

- `at_least` could call a private generator: `return _filter(records, lowest)`. Same effect.
- `count_per_minute` without `groupby`: keep `current_minute` and `count`, yield when the minute
  changes, and yield the last one after the loop. That is exactly what `groupby` saves you from,
  including the easy-to-forget final group.
- In real code, `collections.Counter` replaces the two count dicts and `Counter.most_common` helps
  with the top source (but check its tie rule; it keeps the first seen, not the alphabetical first).
- When you reach the Files module, `parse_lines(open("server.log"))` works unchanged: a file object
  is an iterator of lines.
