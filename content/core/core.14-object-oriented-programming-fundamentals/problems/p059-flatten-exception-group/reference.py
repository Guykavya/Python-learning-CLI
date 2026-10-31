def leaves(eg):
    if not isinstance(eg, BaseExceptionGroup):
        raise TypeError("expected an exception group")
    result = []
    for i, exc in enumerate(eg.exceptions):
        if isinstance(exc, BaseExceptionGroup):
            for path, leaf in leaves(exc):
                result.append(((i,) + path, leaf))
        else:
            result.append(((i,), exc))
    return result


def count_by_type(eg):
    counts = {}
    for _, exc in leaves(eg):
        name = type(exc).__name__
        counts[name] = counts.get(name, 0) + 1
    return counts


def _messages(group):
    if group is None:
        return []
    return [str(exc) for _, exc in leaves(group)]


def partition(eg, exc_type):
    match, rest = eg.split(exc_type)
    return _messages(match), _messages(rest)
