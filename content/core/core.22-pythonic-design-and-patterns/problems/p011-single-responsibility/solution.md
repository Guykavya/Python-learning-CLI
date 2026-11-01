## Approach

Give each job its own function, and let data flow between them:

```
text --parse_order--> rows --validate_order--> errors
                       rows --price_order----> total
```

Each piece now has simple inputs and outputs, so each can be tested alone (no screen needed),
and a change to the error wording touches one function. The only decision left in
`process_order` is "errors or no errors", and it **returns** the text; whoever calls it decides to
print it, send it by email, or show it on a page.

## Code

```python
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
```

## Complexity

Every step is one pass over the rows: O(n) time overall, same as the old function.

## Another way

Split `validate_order` further into one tiny check per rule (`check_fields`, `check_name`, ...)
kept in a list and applied in order; this is the "open for extension" idea of the next problems.
For bigger programs the same split gives layers: parsing, domain rules, presentation.
