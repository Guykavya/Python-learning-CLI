def find_by_attr(db, key, value):
    if value is None or not isinstance(value, (str, int, float, bool)):
        raise ValueError("value must be a string, number or boolean")
    rows = db.execute(
        "SELECT DISTINCT p.id FROM products p, json_each(p.attrs) j WHERE j.key = ? AND j.value = ? ORDER BY p.id",
        (key, value))
    return [r[0] for r in rows]
