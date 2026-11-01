import functools
import types


def _counting(func, counts, name):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        counts[name] += 1
        return func(*args, **kwargs)
    return wrapper


def count_calls(cls):
    counts = {}
    for name, raw in list(vars(cls).items()):
        if name.startswith("__") and name.endswith("__"):
            continue
        if isinstance(raw, (classmethod, staticmethod)):
            counts[name] = 0
            kind = type(raw)                      # classmethod or staticmethod
            setattr(cls, name, kind(_counting(raw.__func__, counts, name)))
        elif isinstance(raw, types.FunctionType):
            counts[name] = 0
            setattr(cls, name, _counting(raw, counts, name))
    cls.call_counts = counts
    return cls


def reset_counts(cls):
    for name in cls.call_counts:
        cls.call_counts[name] = 0
