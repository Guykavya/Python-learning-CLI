from datetime import date, datetime, timedelta


def to_serial(d):
    """Excel serial number (float) of a date or datetime; the time of day is the fraction."""
    raise NotImplementedError


def from_serial(n):
    """The datetime that an Excel serial number stands for."""
    raise NotImplementedError
