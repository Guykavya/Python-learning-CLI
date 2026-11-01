## Approach

Characterization first: the golden table pins the behavior, including odd corners (blank
names, `True` as an amount, ties). Then small safe moves:

1. All the nested validity checks become one function, `_parse_row`, that returns `None` for a bad row. Five identical `skipped += 1` branches become one.
2. The "which row is on top" rule becomes `_is_better_top`, a pure function you can read in one line.
3. Updating one department's numbers becomes `_add_to_stats`.
4. The loop that groups rows becomes `collect`, flat thanks to `continue`.
5. Formatting is split from calculating: `_dept_lines`, `_total_line`, then the thin `legacy_report`.

## Code

```python
def _is_amount(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def _parse_row(row):
    """Return (dept, name, status, amount) for a valid row, or None."""
    name = str(row.get("name") or "").strip()
    dept = str(row.get("dept") or "").strip().title()
    status = row.get("status")
    amount = row.get("amount")
    if not name or not dept or status not in ("paid", "pending") or not _is_amount(amount):
        return None
    return dept, name, status, amount


def _is_better_top(top, name, amount):
    if top is None:
        return True
    return amount > top[1] or (amount == top[1] and name < top[0])


def _add_to_stats(stats, name, status, amount):
    stats["count"] += 1
    stats[status] += amount
    if _is_better_top(stats["top"], name, amount):
        stats["top"] = (name, amount)


def collect(rows):
    depts, skipped = {}, 0
    for row in rows:
        if row.get("status") == "void":
            continue
        parsed = _parse_row(row)
        if parsed is None:
            skipped += 1
            continue
        dept, name, status, amount = parsed
        stats = depts.setdefault(dept, {"count": 0, "paid": 0, "pending": 0, "top": None})
        _add_to_stats(stats, name, status, amount)
    return depts, skipped


def _dept_lines(dept, stats):
    top_name, top_amount = stats["top"]
    return [
        f"== {dept} ==",
        f"  rows: {stats['count']}  paid: {stats['paid']:.2f}  pending: {stats['pending']:.2f}",
        f"  top: {top_name} ({top_amount:.2f})",
    ]


def _total_line(depts):
    paid = sum(stats["paid"] for stats in depts.values())
    pending = sum(stats["pending"] for stats in depts.values())
    return f"TOTAL paid: {paid:.2f}  pending: {pending:.2f}"


def legacy_report(rows):
    depts, skipped = collect(rows)
    lines = ["REPORT"]
    if depts:
        for dept in sorted(depts):
            lines.extend(_dept_lines(dept, depts[dept]))
        lines.append(_total_line(depts))
    else:
        lines.append("no data")
    if skipped:
        lines.append(f"SKIPPED: {skipped}")
    return "\n".join(lines)
```

## Complexity

O(n + d log d) for n rows and d departments (sorting the department names). Same as the
legacy code; the refactor changes the shape, not the cost.

## Another way

Make the three-way split explicit: `clean(rows) -> (valid_rows, skipped)`, `summarise(valid_rows)
-> dict`, `render(summary, skipped) -> str`. Then each stage can be tested on its own, and
`render` never sees a bad row. A `dataclass` for the department stats (`count`, `paid`,
`pending`, `top`) would replace the dict with named attributes. Do that **after** the tests
are green, as a separate step: one kind of change at a time.
