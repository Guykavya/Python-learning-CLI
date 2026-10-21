def sort_records(records, field, *, descending=False):
    """Return records sorted by record[field]; records without the field go last, in order."""
    have = [r for r in records if field in r]
    missing = [r for r in records if field not in r]
    return sorted(have, key=lambda r: r[field], reverse=descending) + missing
