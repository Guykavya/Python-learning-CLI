## Approach

Translate each row of the table into TOML, and each bullet into YAML, then parse the text in the
REPL to check it really means what you think.

TOML points:
- `[tool.ruff.lint]` is a table **inside** `[tool.ruff]`. Since ruff 0.2, rule selection lives
  there (older examples online put `select` directly under `[tool.ruff]`).
- A key with a dot in it (`"__init__.py"`) must be quoted, or TOML reads it as nested tables.
- `[[tool.mypy.overrides]]` (double brackets) appends one table to the **list** `overrides`.
- Booleans are lowercase `true`/`false`; versions like `"3.11"` are strings.

YAML points:
- `repos` is a list (`-`), each repo is a mapping, `hooks` is a list of mappings.
- `false` without quotes is a boolean; `"false"` would be a string (and truthy in Python).
- Version-like values are safer with a `v` or quotes: `rev: 1.10` would be read as the float
  `1.1`.

## Code

```python
PYPROJECT = """\
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.11"
strict = true
files = ["src", "tests"]

[[tool.mypy.overrides]]
module = ["yaml", "yaml.*"]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
"""

PRECOMMIT = """\
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML]
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest -q
        language: system
        pass_filenames: false
        types: [python]
"""
```

In a real project you would then run `pre-commit install` once, and `pre-commit run --all-files`
to check every file (the `rev` values pin tool versions; `pre-commit autoupdate` bumps them).

## Complexity

Not applicable: configuration. The cost to think about is time per commit: ruff takes
milliseconds, mypy seconds, the full test suite possibly much longer, which is why many teams
run pytest in CI instead of in the pre-commit hook.

## Another way

Black and isort can do what `ruff-format` and the `I` rules do. Then the hooks are
`psf/black` and `pycqa/isort`, and `[tool.black]` / `[tool.isort]` (with `profile = "black"`)
go in `pyproject.toml`. Ruff replaces flake8, isort, pyupgrade and black-style formatting with
one fast tool, which is why the plan above uses it.
