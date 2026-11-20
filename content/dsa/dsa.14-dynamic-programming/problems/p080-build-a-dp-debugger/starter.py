import functools


class DPError(Exception):
    """Base class for the debugger's own errors."""


class MissingBaseCase(DPError):
    """The recursion went deeper than max_depth: probably a state that never reaches a base case."""


class CyclicState(DPError):
    """A state needs its own value (directly or through other states): the recursion has a cycle."""


def dp_debug(func=None, *, max_depth=200):
    """Memoise a recursive function and record its table, call counts, depth, missing base cases and cycles.

    Use as @dp_debug or @dp_debug(max_depth=50). The wrapper gets: table, calls, hits, deepest, reset().
    """
    def decorate(f):
        return f            # TODO: return a wrapper (see problem.md)

    if func is not None:
        return decorate(func)
    return decorate
