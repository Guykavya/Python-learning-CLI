# The OLD code: one function parses, validates, prices and prints.
# Your job: split it as described in problem.md. The three stubs below are the new functions.

def parse_order(text):
    raise NotImplementedError


def validate_order(rows):
    raise NotImplementedError


def price_order(rows):
    raise NotImplementedError


def process_order(text):
    """Read an order ('name,qty,price' per line), check it, print the result."""
    rows = []
    for line in text.split("\n"):
        line = line.strip()
        if line != "":
            parts = line.split(",")
            fields = []
            for p in parts:
                fields.append(p.strip())
            rows.append(fields)
    errors = []
    n = 0
    for fields in rows:
        n = n + 1
        if len(fields) != 3:
            errors.append("row " + str(n) + ": expected 3 fields, found " + str(len(fields)))
        elif fields[0] == "":
            errors.append("row " + str(n) + ": name is empty")
        elif not fields[1].isdigit() or int(fields[1]) <= 0:
            errors.append("row " + str(n) + ": quantity must be a whole number above 0")
        else:
            try:
                price = float(fields[2])
            except ValueError:
                price = -1.0
            if price < 0:
                errors.append("row " + str(n) + ": price must be a number, 0 or more")
    if errors:
        for e in errors:
            print(e)
        print("INVALID: " + str(len(errors)) + " problem(s)")
        return
    total = 0.0
    for fields in rows:
        total = total + int(fields[1]) * float(fields[2])
    print("OK: " + str(len(rows)) + " lines, total " + format(round(total, 2), ".2f"))
