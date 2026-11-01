import sys


def deep_size(obj):
    """Bytes of obj plus everything reachable through list/tuple/set/frozenset/dict, each once."""
    # TODO: remember which ids you have already counted, and look inside containers
    return sys.getsizeof(obj)
