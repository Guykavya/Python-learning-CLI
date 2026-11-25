import csv
import math

MISSING = {"", "na", "n/a", "nan", "null", "none", "-", "?"}


def _parse(text):
    t = text.strip().lower()
    if t in MISSING:
        return None
    for junk in ("rs.", "rs", "ms", "%", "$"):
        t = t.replace(junk, "")
    t = t.replace(",", "").replace(" ", "")
    x = float(t)
    if not math.isfinite(x):
        raise ValueError(text)
    return x


def load_column(path, column, low=None, high=None, dedupe_on=None):
    report = {"missing": 0, "unparseable": 0, "out_of_range": 0, "duplicate": 0}
    values = []
    seen = set()
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        names = reader.fieldnames or []
        for name in [column] + list(dedupe_on or []):
            if name not in names:
                raise KeyError(name)
        for row in reader:
            if dedupe_on is not None:
                key = tuple(row[n] for n in dedupe_on)
                if key in seen:
                    report["duplicate"] += 1
                    continue
                seen.add(key)
            try:
                value = _parse(row[column] or "")
            except ValueError:
                report["unparseable"] += 1
                continue
            if value is None:
                report["missing"] += 1
            elif (low is not None and value < low) or (high is not None and value > high):
                report["out_of_range"] += 1
            else:
                values.append(value)
    return values, report
