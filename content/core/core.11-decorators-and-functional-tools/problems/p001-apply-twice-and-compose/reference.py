def apply_twice(f, x):
    return f(f(x))


def compose(f, g):
    def composed(x):
        return f(g(x))
    return composed
