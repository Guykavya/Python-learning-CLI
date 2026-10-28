OPERATORS = ("==", "!=", ">=", "<=", ">", "<")


def to_tuple(version):
    return tuple(int(part) for part in version.strip().split("."))


def pad(a, b):
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)), b + (0,) * (n - len(b))


def compare(a, op, b):
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    if op == ">=":
        return a >= b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    return a < b


def satisfies(version, spec):
    v = to_tuple(version)
    for clause in spec.split(","):
        clause = clause.strip()
        if not clause:
            continue
        for op in OPERATORS:
            if clause.startswith(op):
                break
        else:
            raise ValueError(f"unknown operator in {clause!r}")
        rest = clause[len(op):].strip()
        if not rest or rest[0] in "=<>!~":
            raise ValueError(f"unknown operator in {clause!r}")
        a, b = pad(v, to_tuple(rest))
        if not compare(a, op, b):
            return False
    return True
