import operator
from functools import reduce


def pick(rows, *indexes):
    if not indexes:
        raise ValueError("pick needs at least one index")
    getter = operator.itemgetter(*indexes)
    if len(indexes) == 1:
        return [(getter(row),) for row in rows]
    return [getter(row) for row in rows]


def call_method(items, name, *args):
    caller = operator.methodcaller(name, *args)
    return list(map(caller, items))


def get_path(data, *keys, default=None):
    try:
        return reduce(operator.getitem, keys, data)
    except (KeyError, IndexError, TypeError):
        return default
