import builtins
import dis
import types


def globals_used(func):
    """Sorted unique names loaded with LOAD_GLOBAL, including nested code objects."""
    # TODO: walk dis.get_instructions(...) and keep the argval of LOAD_GLOBAL instructions.
    # Warning: co_names is NOT the answer (it also holds attribute names).
    return sorted(func.__code__.co_names)


def undefined_globals(func):
    """Names from globals_used(func) that are neither module globals nor builtins."""
    # TODO
    return []
