## Approach

Three small ideas:

1. **Normalise first.** `pip freeze` prints names as the project spells them (`Flask`, `Typing_Extensions`).
   Build a new dict with normalised keys once, then every lookup is exact.
2. **Check each requirement** with `satisfies` from p013. Record a problem and remember the name in a
   `failed` set; remember passing names in an `ok` set.
3. **Lock** the names that passed and never failed: `sorted(ok - failed)`. Sets also remove duplicates,
   so a name with two requirement lines is locked once.

Why a lock file at all? The specifier `>=2.31,<3` allows many versions. Today you get 2.32.3; next month a
fresh install may get 2.33.0. A lock file turns "allowed" into "exactly this", so your laptop, your
friend's laptop and the server all run what you tested.

## Code

```python
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
```

## Complexity

O(i + r·c + k log k): normalising i installed names, checking r requirements with c clauses each, and
sorting k locked names.

## Another way

In a real project you would put `satisfies` in its own module (`versions.py`) and `from versions import
satisfies` here, instead of copying it: one tested copy, many users. Real lock tools also go further:
`pip freeze > requirements.lock`, `uv lock` and `poetry lock` pin **every** installed package, including
dependencies of dependencies, and lock files from `uv` and `poetry` also store a hash of each file, so a
changed download is detected.
