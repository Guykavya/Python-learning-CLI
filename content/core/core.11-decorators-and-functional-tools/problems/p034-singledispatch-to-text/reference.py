from functools import singledispatch


@singledispatch
def to_text(value):
    raise TypeError(f"cannot convert {type(value).__name__}")


@to_text.register(int)
def _(value):
    return str(value)


@to_text.register(bool)
def _(value):
    return "yes" if value else "no"


@to_text.register(float)
def _(value):
    return f"{value:.2f}"


@to_text.register(str)
def _(value):
    return f'"{value}"'


@to_text.register(type(None))
def _(value):
    return "null"


@to_text.register(list)
def _(value):
    return "[" + ", ".join(to_text(item) for item in value) + "]"


@to_text.register(tuple)
def _(value):
    inner = ", ".join(to_text(item) for item in value)
    if len(value) == 1:
        inner += ","
    return "(" + inner + ")"


@to_text.register(dict)
def _(value):
    pairs = [f"{to_text(k)}: {to_text(v)}" for k, v in value.items()]
    return "{" + ", ".join(pairs) + "}"
