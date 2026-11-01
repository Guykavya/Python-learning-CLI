def parse_order(text):
    rows = []
    for line in text.split("\n"):
        line = line.strip()
        if line:
            rows.append([part.strip() for part in line.split(",")])
    return rows


def _row_error(fields):
    if len(fields) != 3:
        return f"expected 3 fields, found {len(fields)}"
    name, qty, price = fields
    if name == "":
        return "name is empty"
    if not qty.isdigit() or int(qty) <= 0:
        return "quantity must be a whole number above 0"
    try:
        ok = float(price) >= 0
    except ValueError:
        ok = False
    return None if ok else "price must be a number, 0 or more"


def validate_order(rows):
    errors = []
    for n, fields in enumerate(rows, start=1):
        problem = _row_error(fields)
        if problem:
            errors.append(f"row {n}: {problem}")
    return errors


def price_order(rows):
    return round(sum(int(qty) * float(price) for _, qty, price in rows), 2)


def process_order(text):
    rows = parse_order(text)
    errors = validate_order(rows)
    if errors:
        return "\n".join(errors + [f"INVALID: {len(errors)} problem(s)"])
    return f"OK: {len(rows)} lines, total {price_order(rows):.2f}"
