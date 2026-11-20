def conflicting_facts(rows, key, field):
    seen = {}
    for row in rows:
        values = seen.setdefault(row[key], [])
        if row[field] not in values:
            values.append(row[field])
    return {k: v for k, v in seen.items() if len(v) > 1}
