from itertools import groupby


def day_of(line):
    return line.split()[0]


def count_by_day(lines):
    records = (line.strip() for line in lines)
    records = (line for line in records if line)
    counts = {}
    for day, group in groupby(sorted(records, key=day_of), key=day_of):
        counts[day] = len(list(group))
    return counts
