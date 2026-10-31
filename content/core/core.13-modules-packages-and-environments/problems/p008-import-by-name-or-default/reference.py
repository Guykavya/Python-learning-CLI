import importlib


def import_or_default(name, default=None):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as e:
        if e.name == name or name.startswith(f"{e.name}."):
            return default
        raise
