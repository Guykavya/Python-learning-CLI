def all_constants(source, mode="exec"):
    """Every constant in the compiled source, including nested code objects (but not the code objects)."""
    code = compile(source, "<src>", mode)
    # TODO: also look inside nested code objects found in co_consts
    return list(code.co_consts)


def is_folded(expr, value):
    """True if compiling expr produced a constant equal to value and of the same type."""
    # TODO
    return False
