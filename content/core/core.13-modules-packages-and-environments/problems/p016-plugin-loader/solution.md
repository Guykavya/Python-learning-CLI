## Approach

A plugin system must import files whose names it learns at run time. `importlib.util` loads a module
from a path in three steps: make a *spec* (where the file is and what the module is called), make an
empty module from the spec, and run the file's code inside it with `exec_module`. This does not use
`sys.path` and does not store the module in `sys.modules`, so every call loads the current file again.

Errors in a plugin are the plugin's problem, not the loader's: catch `Exception` around the load and
record the stem. `getattr(module, "register", None)` with `callable` finds the entry function safely.

## Code

```python
import importlib.util
from pathlib import Path


def load_module_from_file(path: Path):
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
```

## Complexity

O(n log n) to sort n files, plus the time to run each plugin's top-level code.

## Another way

Put the folder on `sys.path` and use `importlib.import_module(stem)`. It is shorter, but the module
cache returns the old module after a file changes, a plugin called `json.py` would shadow the standard
library, and the folder stays on `sys.path` for the whole program. Real tools that need plugins from
installed packages use *entry points* instead (`importlib.metadata.entry_points(group=...)`), which is
the same "name -> callable" idea as problem p017.
