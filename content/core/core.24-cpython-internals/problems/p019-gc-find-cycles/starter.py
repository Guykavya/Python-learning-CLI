import gc
import types


def cycle_path(obj, max_depth=100):
    """Shortest [obj, ..., obj] path through gc.get_referents, or None."""
    # TODO: breadth-first search from obj's referents, remembering how you reached each object.
    # Skip classes, modules and plain functions.
    return None


def in_cycle(obj, max_depth=100):
    """True if obj can reach itself by following referents."""
    return cycle_path(obj, max_depth) is not None
