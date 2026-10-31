- **`[tool.mypy.overrides]` with single brackets.** That makes a single table, not a list; mypy
  expects a list of override tables.
- **`select` under `[tool.ruff]`.** Older ruff accepted it; current ruff warns and expects
  `[tool.ruff.lint]`.
- **Unquoted `__init__.py` as a key.** TOML splits it at the dot into nested tables.
- **`python_version = 3.11` without quotes.** That is a float; `3.10` would even become `3.1`.
- **`pass_filenames: "false"`.** A quoted string, so pre-commit sees a non-empty value and the
  test run gets every changed file name as an argument.
- **ruff-format before ruff --fix.** The fixer may change code after it was formatted, and the
  next commit shows formatting changes again.
- **Tabs in YAML.** YAML indentation must be spaces.
- **Forgetting `additional_dependencies` for mypy.** pre-commit installs mypy in an isolated
  environment, so imports of third-party packages have no type information there.
