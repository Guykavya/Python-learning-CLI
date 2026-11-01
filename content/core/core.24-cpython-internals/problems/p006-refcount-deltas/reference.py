import sys


def extra_refs(store):
    """How many references store(obj) adds to a brand-new object."""
    obj = object()
    before = sys.getrefcount(obj)
    kept = store(obj)
    after = sys.getrefcount(obj)
    del kept
    return after - before
