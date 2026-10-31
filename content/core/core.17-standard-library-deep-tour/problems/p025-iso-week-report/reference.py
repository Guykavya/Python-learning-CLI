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
