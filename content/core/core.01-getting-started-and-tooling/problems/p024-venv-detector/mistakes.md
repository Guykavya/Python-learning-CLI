- Typing `True`: correct in one run, wrong in the other. The tests run both.
- Checking `os.environ.get("VIRTUAL_ENV")`: only set by `activate`, not when the
  venv's Python is run by path.
- Comparing `sys.executable` with `/usr/bin/python3`: breaks on any machine
  where Python lives elsewhere.
- Writing `sys.prefix =! sys.base_prefix`: that is a syntax error. The operator
  is `!=`.
