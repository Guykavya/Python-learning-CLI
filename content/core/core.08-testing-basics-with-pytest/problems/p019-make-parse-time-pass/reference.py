def parse_time(text):
    """Turn 'H:MM' into minutes. Raise ValueError for bad text."""
    parts = text.strip().split(":")
    if len(parts) != 2:
        raise ValueError("expected H:MM, like 1:30")
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
    except ValueError:
        raise ValueError("hours and minutes must be whole numbers") from None
    if minutes < 0 or minutes > 59:
        raise ValueError("minutes must be 0 to 59")
    return hours * 60 + minutes
