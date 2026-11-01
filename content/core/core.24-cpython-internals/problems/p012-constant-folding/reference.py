CodeType = type(compile("", "<src>", "exec"))


def all_constants(source, mode="exec"):
    """Every constant in the compiled source, including nested code objects (but not the code objects)."""
    found = []
    todo = [compile(source, "<src>", mode)]
    while todo:
        code = todo.pop()
        for const in code.co_consts:
            if isinstance(const, CodeType):
                todo.append(const)
            else:
                found.append(const)
    return found


def is_folded(expr, value):
    """True if compiling expr produced a constant equal to value and of the same type."""
    for const in all_constants(expr, "eval"):
        if type(const) is type(value) and const == value:
            return True
    return False
