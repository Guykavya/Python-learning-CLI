def compose(*funcs):
    """Return a function x -> funcs[0](funcs[1](...funcs[-1](x)))."""
    def composed(x):
        for f in reversed(funcs):
            x = f(x)
        return x
    return composed
