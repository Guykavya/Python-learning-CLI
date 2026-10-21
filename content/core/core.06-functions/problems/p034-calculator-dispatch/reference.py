def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    """Return a / b, or None when b is 0."""
    if b == 0:
        return None
    return a / b


OPERATIONS = {"+": add, "-": subtract, "*": multiply, "/": divide}


def calculate(a, op, b):
    """Look up op in OPERATIONS and apply it to a and b; None for an unknown op."""
    func = OPERATIONS.get(op)
    if func is None:
        return None
    return func(a, b)
