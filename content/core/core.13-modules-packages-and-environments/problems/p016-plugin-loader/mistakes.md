- Using `import_module` after adding the folder to `sys.path`. The cache returns the old code, and the
  folder can shadow real modules (`plugins/json.py` would replace the standard `json`).
- Catching only `ImportError`. A plugin's own code can raise anything (`ZeroDivisionError`,
  `SyntaxError`, `KeyError`). Catch `Exception`.
- Using `module.register` directly. A module without `register` raises `AttributeError`; use
  `getattr(module, "register", None)` and `callable(...)`.
- Using `rglob` or `iterdir` without a suffix check: sub-folders and `.txt` files are not plugins.
- Relying on the order of `glob`. It follows the file system, which is not sorted. Sort the paths.
- Using the same module name for every plugin and storing it in `sys.modules`: later plugins overwrite
  earlier ones.
