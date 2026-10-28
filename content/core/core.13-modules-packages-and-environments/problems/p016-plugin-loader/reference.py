import importlib.util
from pathlib import Path


def load_module_from_file(path: Path):
    """Load one file as a new module object, without sys.path and without the cache."""
    spec = importlib.util.spec_from_file_location(f"plugin_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_plugins(folder):
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"no plugin folder: {folder}")
    plugins = {}
    failed = []
    for path in sorted(folder.glob("*.py")):
        if path.name.startswith("_"):
            continue
        try:
            module = load_module_from_file(path)
        except Exception:
            failed.append(path.stem)
            continue
        register = getattr(module, "register", None)
        if callable(register):
            plugins[path.stem] = register
    return plugins, sorted(failed)


def run_plugins(folder, app):
    plugins, _failed = load_plugins(folder)
    called = []
    for name, register in plugins.items():
        register(app)
        called.append(name)
    return called
