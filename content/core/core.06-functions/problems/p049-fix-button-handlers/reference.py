def make_click(name):
    """Return a handler that remembers this name in its own scope."""
    def handler():
        return "Clicked " + name
    return handler


def make_handlers(names):
    """Return {name: handler}; each handler takes no arguments and returns 'Clicked <name>'."""
    handlers = {}
    for name in names:
        handlers[name] = make_click(name)
    return handlers


def make_adder(i):
    """Return a function that adds i."""
    return lambda x: x + i


def make_adders(n):
    """Return [f0, f1, ...]; f_i(x) returns x + i."""
    return [make_adder(i) for i in range(n)]
