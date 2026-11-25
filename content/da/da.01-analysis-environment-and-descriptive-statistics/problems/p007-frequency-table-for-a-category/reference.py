from collections import Counter


def frequency_table(values):
    labels = ["(missing)" if v is None or v == "" else v for v in values]
    total = len(labels)
    counts = Counter(labels)
    rows = [(v, c, round(100 * c / total, 1)) for v, c in counts.items()]
    rows.sort(key=lambda r: (-r[1], r[0]))
    return rows
