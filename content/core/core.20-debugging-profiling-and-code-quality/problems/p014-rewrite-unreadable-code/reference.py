def summarise_orders(rows: list[str]) -> list[tuple[str, int, float]]:
    """Total quantity and revenue per product from CSV-like order rows.

    Each row is "name,quantity,unit_price". Rows that are empty, start with "#", do not have
    exactly three fields, have a quantity that is not an int or a price that is not a float,
    or have a quantity <= 0 are skipped. Names are compared after strip() and lower().

    Returns (name, total_quantity, revenue rounded to 2 places) tuples, highest revenue
    first, ties by name.
    """
    totals: dict[str, list] = {}  # name -> [quantity, revenue]
    for row in rows:
        if not row or row.startswith("#"):
            continue
        fields = row.split(",")
        if len(fields) != 3:
            continue
        name_text, qty_text, price_text = fields
        try:
            quantity = int(qty_text)
            price = float(price_text)
        except ValueError:
            continue
        if quantity <= 0:
            continue
        name = name_text.strip().lower()
        entry = totals.setdefault(name, [0, 0.0])
        entry[0] += quantity
        entry[1] += quantity * price

    summary = [(name, qty, round(revenue, 2)) for name, (qty, revenue) in totals.items()]
    summary.sort(key=lambda item: (-item[2], item[0]))
    return summary
