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
    """Group valid rows by department. Returns (stats_by_dept, skipped_count)."""
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
