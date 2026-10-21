- `print("Python:", version, "(", implementation, ")")` gives
  `Python: 3.14.4 ( CPython )`.
- `os.environ["USER"]` crashes with `KeyError` when `USER` is not set (common in
  containers and some cron jobs). Use `.get` with a default.
- Putting the docstring above the shebang. The shebang must be line 1, and the
  docstring must be the first *statement* (comments do not count, so the shebang
  does not get in its way).
- Printing `In venv: True` as fixed text instead of computing it.
