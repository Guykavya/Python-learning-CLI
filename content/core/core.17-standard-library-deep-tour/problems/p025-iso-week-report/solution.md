## Approach

Let the standard library do the calendar maths. `isocalendar()` knows the ISO rules (Monday
start, week 1 contains the first Thursday), and its `year` field is the **ISO year**, which differs
from `d.year` for a few days around New Year. `fromisocalendar()` is the reverse and also
validates: week 53 of a 52-week year raises `ValueError`.

For the report, group with two dicts keyed by the week key: one adds the hours, one collects a
`set` of dates so that two entries on the same day count as one day. The key `"YYYY-Www"` is
zero-padded, so sorting the keys as text also sorts them in time order.

## Code

```python
from datetime import date, timedelta


def week_key(d: date) -> str:
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def week_start(key: str) -> date:
    year_text, sep, week_text = key.partition("-W")
    if not sep or len(year_text) != 4 or len(week_text) != 2:
        raise ValueError(f"not a week key like '2025-W01': {key!r}")
    return date.fromisocalendar(int(year_text), int(week_text), 1)


def weekly_report(entries: list[tuple[str, float]]) -> list[str]:
    totals: dict[str, float] = {}
    days: dict[str, set[date]] = {}
    for text, hours in entries:
        d = date.fromisoformat(text)
        key = week_key(d)
        totals[key] = totals.get(key, 0.0) + hours
        days.setdefault(key, set()).add(d)
    lines = []
    for key in sorted(totals):
        monday = week_start(key)
        sunday = monday + timedelta(days=6)
        n = len(days[key])
        word = "day" if n == 1 else "days"
        lines.append(f"{key} {monday.isoformat()}..{sunday.isoformat()}: {totals[key]:.1f} h on {n} {word}")
    return lines
```

## Complexity

O(n + w log w) for n entries and w different weeks (the sort). Memory O(n) for the date sets.

## Another way

`d.strftime("%G-W%V")` formats the ISO year and week directly (`%G` is the ISO year, `%V` the ISO
week). Be careful: `%Y` and `%W` look similar but are **not** ISO (`%W` counts weeks from the
first Monday, starting at 0). The grouping could also use `collections.defaultdict(float)` and
`defaultdict(set)` from earlier in this chapter.
