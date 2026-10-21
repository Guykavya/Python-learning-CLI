def make_handlers(names):
    """Return {name: handler}; each handler takes no arguments and returns 'Clicked <name>'."""
    handlers = {}
    for name in names:
        handlers[name] = lambda: "Clicked " + name
    return handlers


def make_adders(n):
    """Return [f0, f1, ...]; f_i(x) returns x + i."""
    return [lambda x: x + i for i in range(n)]
