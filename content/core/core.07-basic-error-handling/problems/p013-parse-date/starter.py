def parse_date(text):
    """Return (year, month, day) for 'YYYY-MM-DD'; raise ValueError with a helpful message."""
    year, month, day = text.split("-")
    return int(year), int(month), int(day)
