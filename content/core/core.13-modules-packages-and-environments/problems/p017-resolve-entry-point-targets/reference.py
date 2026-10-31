import importlib


def resolve(target):
    if target.count(":") != 1:
        raise ValueError(f"target must look like 'module:attribute', got {target!r}")
    module_name, attr_path = target.split(":")
    parts = attr_path.split(".")
    if not module_name or "" in module_name.split(".") or "" in parts:
        raise ValueError(f"empty name in target {target!r}")
    obj = importlib.import_module(module_name)
    for name in parts:
        try:
            obj = getattr(obj, name)
        except AttributeError:
            raise AttributeError(f"{target!r}: no attribute {name!r}") from None
    return obj


def dispatch(table, command, args):
    target = table[command]
    func = resolve(target)
    if not callable(func):
        raise TypeError(f"{target!r} is not callable")
    return func(args)
