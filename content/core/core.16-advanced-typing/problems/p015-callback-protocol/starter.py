def fixed(value, precision=2):
    return str(value)


def percent(value, precision=2):
    return str(value)


def format_all(values, fmt, precision=2):
    return [fmt(v) for v in values]
