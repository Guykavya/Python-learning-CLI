FACTORS = {"g": 0.001, "kg": 1.0, "lb": 0.45359237}


def to_kg(values, units):
    """Convert each value to kilograms using its unit; unknown unit -> ValueError naming it."""
    out = []
    for value, unit in zip(values, units):
        key = str(unit).strip().lower()
        if key not in FACTORS:
            raise ValueError("unknown unit %r" % str(unit).strip())
        if value is None or value != value:
            out.append(float("nan"))
        else:
            out.append(float(value) * FACTORS[key])
    return out
