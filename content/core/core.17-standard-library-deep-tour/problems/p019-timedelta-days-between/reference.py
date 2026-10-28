from datetime import date, timedelta


def days_between(a: date, b: date) -> int:
    return abs((b - a).days)


def add_business_days(start: date, n: int) -> date:
    step = timedelta(days=1 if n >= 0 else -1)
    day = start
    left = abs(n)
    while left > 0:
        day += step
        if day.weekday() < 5:
            left -= 1
    return day


def age_on(birth: date, today: date) -> int:
    years = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        years -= 1
    return years


def format_duration(td: timedelta) -> str:
    if td < timedelta(0):
        raise ValueError(f"negative duration: {td}")
    hours, rest = divmod(td.seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{td.days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
