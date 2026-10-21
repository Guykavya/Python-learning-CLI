BINARY = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}


def evaluate(expr):
    """Return the value of a number or a nested (op, left, right) / ('neg', x) tuple."""
    if not isinstance(expr, tuple):
        return expr
    if expr[0] == "neg":
        return -evaluate(expr[1])
    op, left, right = expr
    return BINARY[op](evaluate(left), evaluate(right))


def to_text(expr):
    """Return expr as a fully parenthesised string."""
    if not isinstance(expr, tuple):
        return str(expr)
    if expr[0] == "neg":
        return "-" + to_text(expr[1])
    op, left, right = expr
    return f"({to_text(left)} {op} {to_text(right)})"
