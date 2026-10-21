def parse_time(text):
    """Turn 'H:MM' into minutes. Raise ValueError for bad text."""
    hours, minutes = text.split(":")
    return int(hours) * 60 + int(minutes)
