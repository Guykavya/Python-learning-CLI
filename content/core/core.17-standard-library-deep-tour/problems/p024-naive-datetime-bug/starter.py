"""Shift log for a hospital that has wards in several cities.

Users report: night-shift pay is wrong twice a year, the UTC times in the export are wrong
for some wards, and the overdue list is wrong for the Kolkata office.
All four functions run without errors. Find the bugs and fix them.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

FMT = "%Y-%m-%d %H:%M"


def parse_local(text, zone):
    """'2024-10-26 22:00' read as a wall-clock time in `zone` (e.g. 'Europe/London').

    Returns an AWARE datetime. A wall time that does not exist in that zone (skipped
    when the clocks went forward) raises ValueError. A repeated time means the first one.
    """
    return datetime.strptime(text, FMT)


def to_utc_iso(text, zone):
    """The same moment in UTC, as an ISO string: '2024-07-01T03:30:00+00:00'."""
    local = parse_local(text, zone)
    return local.astimezone(timezone.utc).isoformat()


def shift_hours(start_text, end_text, zone):
    """Hours really worked between two wall-clock times in `zone`."""
    start = parse_local(start_text, zone)
    end = parse_local(end_text, zone)
    return (end - start).total_seconds() / 3600


def is_overdue(due_iso, now):
    """True if the moment `now` is after the due moment.

    due_iso has an offset ('2024-05-01T12:00:00+00:00'); now is an aware datetime.
    A naive `now` (or due time) is a programming error: raise ValueError.
    """
    due = datetime.fromisoformat(due_iso)
    # comparing naive and aware raised TypeError, so the tzinfo is dropped here
    return due.replace(tzinfo=None) < now.replace(tzinfo=None)
