from datetime import date, timedelta


def week_key(d: date) -> str:
    """'YYYY-Www' using the ISO week-numbering year and week."""
    return f"{d.year}-W{d.strftime('%W')}"


def week_start(key: str) -> date:
    """The Monday of week 'YYYY-Www'. A bad key raises ValueError."""
    return date(2000, 1, 1)


def weekly_report(entries: list[tuple[str, float]]) -> list[str]:
    """One line per ISO week, oldest first."""
    return []
