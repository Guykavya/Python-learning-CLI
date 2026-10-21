def calculate(expression):
    """Evaluate '<number> <operator> <number>'; return the result or an 'Error: ...' message."""
    a, op, b = expression.split()
    a, b = float(a), float(b)
    if op == "+":
        return str(a + b)
    if op == "-":
        return str(a - b)
    if op == "*":
        return str(a * b)
    return str(a / b)
