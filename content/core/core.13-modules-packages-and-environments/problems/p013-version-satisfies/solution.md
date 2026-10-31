## Approach

Three small steps make this easy:

1. `to_tuple("1.10.2")` → `(1, 10, 2)`. Tuples compare item by item, which is exactly how version
   numbers work. Strings compare character by character, so `"1.10" < "1.9"` (because `"1" < "9"`).
2. Split the spec on commas. For each clause, find the operator by checking the start of the text. The
   two-character operators must be checked **before** `>` and `<`, or `">=1.2"` is read as `>` with
   version `"=1.2"`. After the operator, the rest must be a version; if it still starts with `=`, `<`,
   `>`, `!` or `~` the operator was not valid (`=>`, `<>`), so raise `ValueError`.
3. Pad both tuples to the same length with zeros and compare. One failing clause is enough to say `False`.

## Code

```python
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
```

The `for ... else` runs the `else` only when the loop did **not** `break`, that is, when no operator matched.
A version like `"1.x"` makes `int()` raise `ValueError` by itself, which is also fine.

## Complexity

O(c · k) for c clauses and versions with k parts.

## Another way

Replace the `if` chain in `compare` with a dict of functions from the `operator` module:
`{"==": operator.eq, ">=": operator.ge, ...}[op](a, b)`. Real tools use
`packaging.version.Version` and `packaging.specifiers.SpecifierSet`, which also understand `~=`, `===`,
pre-releases like `2.0rc1`, and wildcards like `==1.2.*`.
