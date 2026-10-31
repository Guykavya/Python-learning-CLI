from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def show_in_zones(when: datetime, zones: list[str]) -> list[str]:
    if when.tzinfo is None or when.utcoffset() is None:
        raise ValueError("when must be an aware datetime (it has no time zone)")
    lines = []
    for name in zones:
        local = when.astimezone(ZoneInfo(name))
        lines.append(f"{name}: {local:%Y-%m-%d %H:%M} {local.tzname()}")
    return lines


def common_hours(day: date, zones: list[str], start_hour: int = 9, end_hour: int = 17) -> list[datetime]:
    tzs = [ZoneInfo(name) for name in zones]
    first = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    result = []
    for h in range(24):
        slot = first + timedelta(hours=h)
        ok = True
        for tz in tzs:
            local = slot.astimezone(tz)
            minutes = local.hour * 60 + local.minute
            if minutes < start_hour * 60 or minutes + 60 > end_hour * 60:
                ok = False
                break
        if ok:
            result.append(slot)
    return result
