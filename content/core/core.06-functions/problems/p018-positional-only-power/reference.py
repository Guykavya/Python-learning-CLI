def power(base, exp, /, *, modulo=None):
    """Return base ** exp, reduced modulo `modulo` when it is given."""
    if modulo is None:
        return base ** exp
    return pow(base, exp, modulo)
