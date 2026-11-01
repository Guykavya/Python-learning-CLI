def code_facts(func):
    """Return name, argcount, locals, names and constants of func's code object."""
    code = func.__code__
    return {
        "name": code.co_name,
        "argcount": code.co_argcount,
        "locals": sorted(code.co_varnames),
        "names": sorted(code.co_names),
        "constants": [c for c in code.co_consts if c is not None],
    }
