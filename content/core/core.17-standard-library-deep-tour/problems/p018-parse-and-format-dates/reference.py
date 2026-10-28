from datetime import date, datetime


def parse_log_stamp(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")


def parse_us_date(text: str) -> date:
    return datetime.strptime(text, "%m/%d/%Y").date()


def to_iso(dt: datetime) -> str:
    return dt.isoformat()


def pretty(dt: datetime) -> str:
    return f"{dt:%a} {dt.day} {dt:%b %Y, %H:%M}"
