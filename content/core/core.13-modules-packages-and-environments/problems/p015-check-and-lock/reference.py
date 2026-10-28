OPERATORS = ("==", "!=", ">=", "<=", ">", "<")


def normalise(name):
    return name.lower().replace("_", "-").replace(".", "-")


def to_tuple(version):
    return tuple(int(part) for part in version.strip().split("."))


def compare(a, op, b):
    n = max(len(a), len(b))
    a = a + (0,) * (n - len(a))
    b = b + (0,) * (n - len(b))
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
        if not compare(v, op, to_tuple(clause[len(op):])):
            return False
    return True


def make_lock(requirements, installed):
    versions = {normalise(name): version for name, version in installed.items()}
    problems = []
    failed = set()
    ok = set()
    for name, spec in requirements:
        if name not in versions:
            problems.append(f"{name}: not installed")
            failed.add(name)
        elif not satisfies(versions[name], spec):
            problems.append(f"{name}: {versions[name]} does not satisfy {spec}")
            failed.add(name)
        else:
            ok.add(name)
    lock = [f"{name}=={versions[name]}" for name in sorted(ok - failed)]
    return lock, problems
