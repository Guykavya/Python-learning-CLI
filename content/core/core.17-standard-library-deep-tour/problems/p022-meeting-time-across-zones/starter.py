from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def show_in_zones(when: datetime, zones: list[str]) -> list[str]:
    """One line per zone: 'Zone/Name: YYYY-MM-DD HH:MM ABBR'. A naive `when` raises ValueError."""
    return []


def common_hours(day: date, zones: list[str], start_hour: int = 9, end_hour: int = 17) -> list[datetime]:
    """UTC hour slots on `day` that fit inside working hours in every zone."""
    return []
