def call_all(funcs, value):
    """Return [f(value) for each f in funcs]."""
    results = []
    for f in funcs:
        results.append(f(value))
    return results


CHECKS = [len, str.upper, str.isdigit]


def describe(value):
    """Return call_all(CHECKS, value)."""
    return call_all(CHECKS, value)
