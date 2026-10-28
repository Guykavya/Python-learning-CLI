from functools import singledispatch


@singledispatch
def describe(x):
    return f"unknown: {x!r}"


@describe.register
def _(x: int):
    kind = "even" if x % 2 == 0 else "odd"
    return f"int {x} ({kind})"


@describe.register
def _(x: bool):
    return f"bool {x}"


@describe.register
def _(x: str):
    return f"text {x!r} of length {len(x)}"


@describe.register
def _(x: list):
    inner = ", ".join(describe(item) for item in x)
    return f"list of {len(x)}: [{inner}]"
