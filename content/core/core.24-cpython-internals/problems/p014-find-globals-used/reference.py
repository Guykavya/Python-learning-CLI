import builtins
import dis
import types


def _global_loads(code):
    """Set of names loaded with LOAD_GLOBAL in code and every nested code object."""
    names = {ins.argval for ins in dis.get_instructions(code) if ins.opname == "LOAD_GLOBAL"}
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            names |= _global_loads(const)
    return names


def globals_used(func):
    """Sorted unique names loaded with LOAD_GLOBAL, including nested code objects."""
    return sorted(_global_loads(func.__code__))


def undefined_globals(func):
    """Names from globals_used(func) that are neither module globals nor builtins."""
    known_builtins = vars(builtins)
    return [
        name for name in globals_used(func)
        if name not in func.__globals__ and name not in known_builtins
    ]
