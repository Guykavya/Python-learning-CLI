import re

DATE_RE = re.compile(
    r"\b(?:([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})|([0-9]{4})-([0-9]{2})-([0-9]{2}))\b"
)


def find_dates(text: str) -> list[str]:
    result = []
    for m in DATE_RE.finditer(text):
        if m.group(1) is not None:
            day, month, year = m.group(1), m.group(2), m.group(3)
        else:
            year, month, day = m.group(4), m.group(5), m.group(6)
        d, mo = int(day), int(month)
        if 1 <= mo <= 12 and 1 <= d <= 31:
            result.append(f"{year}-{mo:02d}-{d:02d}")
    return result
