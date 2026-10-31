from datetime import date, datetime


def parse_log_stamp(text: str) -> datetime:
    return datetime(2000, 1, 1)


def parse_us_date(text: str) -> date:
    return date(2000, 1, 1)


def to_iso(dt: datetime) -> str:
    return ""


def pretty(dt: datetime) -> str:
    return ""
