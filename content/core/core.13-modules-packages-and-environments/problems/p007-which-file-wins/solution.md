## Approach

Copy the rule Python uses. The outer loop goes over the folders in order, because the first folder with
any match wins. Inside a folder, check the package form `name/__init__.py` first, then `name.py`.
`Path.is_file()` answers both questions and is `False` for missing paths, so missing folders need no
special code.

## Code

```python
from pathlib import Path


def find_module_file(name, folders):
    for folder in folders:
        base = Path(folder)
        package = base / name / "__init__.py"
        if package.is_file():
            return package
        module = base / f"{name}.py"
        if module.is_file():
            return module
    return None
```

## Complexity

O(f) file checks for f folders: at most two per folder.

## Another way

Ask Python itself: `importlib.util.find_spec(name)` searches the real `sys.path` and returns a spec whose
`origin` is the file path (or `None` if the module is missing). `importlib.machinery.PathFinder.find_spec(name, folders)`
does the same for your own list of folders. When a module "behaves strangely", `print(module.__file__)`
shows at once which file was loaded.
