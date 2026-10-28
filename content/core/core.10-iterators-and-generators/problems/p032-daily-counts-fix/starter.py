from itertools import groupby


def day_of(line: str) -> str:
    # "2026-10-05 login ann" -> "2026-10-05"
    return line.split()[0]


def count_by_day(lines) -> dict[str, int]:
    records = (line.strip() for line in lines)
    records = (line for line in records if line)   # skip blank lines
    counts = {}
    for day, group in groupby(records, key=day_of):
        counts[day] = len(list(group))
    return counts
