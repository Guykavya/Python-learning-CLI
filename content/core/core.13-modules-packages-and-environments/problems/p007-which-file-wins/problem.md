# Which file does `import` load?

When you write `import name`, Python walks through the folders of `sys.path` **in order** and stops at
the **first** folder that has a match. Inside one folder, a **package** (a folder `name/` with an
`__init__.py`) is checked before a **module** file `name.py`.

This is why a file `random.py` next to your script hides the real `random` module: the script's own
folder is first in `sys.path`.

Write `find_module_file(name, folders)` in `solution.py`. `folders` is a list of folder paths (`str` or
`Path`) in search order. Return a `pathlib.Path`:

- `folder / name / "__init__.py"` if that file exists in the folder, else
- `folder / name + ".py"` if that file exists,
- checking the folders one by one, and returning the first match.

Return `None` if no folder has a match. Folders in the list that do not exist are skipped.
A folder `name/` **without** `__init__.py` does not count here. (Real Python can use it as a
"namespace package", but only if nothing else matches anywhere. We leave that out.)

**Example**

```text
project/                lib/
├── random.py           ├── random.py
└── shop/               └── shop.py
    └── __init__.py
```

```python
find_module_file("random", ["project", "lib"])   # Path("project/random.py")   project is first
find_module_file("shop", ["project", "lib"])     # Path("project/shop/__init__.py")
find_module_file("shop", ["lib", "project"])     # Path("lib/shop.py")          lib is first now
find_module_file("nothing", ["project", "lib"])  # None
```
