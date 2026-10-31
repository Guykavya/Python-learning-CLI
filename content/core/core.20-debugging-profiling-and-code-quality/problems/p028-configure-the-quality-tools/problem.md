# Configure the quality tools

Quality tools are only useful when **everyone** runs them with the **same settings**. So the
settings live in files that are committed with the code: `pyproject.toml` for ruff, mypy and
pytest, and `.pre-commit-config.yaml` for the hooks that run before every `git commit`.

In `solution.py` write two string constants that hold the **text** of those two files. The tests
parse them with `tomllib` and `yaml.safe_load` and check the values (they never run ruff, mypy or
pre-commit, so you do not need them installed).

**`PYPROJECT`** (TOML) must contain:

| Table | Settings |
|---|---|
| `[tool.ruff]` | `line-length` 100, `target-version` `"py311"` |
| `[tool.ruff.lint]` | `select` exactly the rule groups `E`, `F`, `W`, `I`, `B`, `UP`; `ignore` `["E501"]` |
| `[tool.ruff.lint.per-file-ignores]` | files matching `"__init__.py"` ignore `["F401"]` (re-exports look like unused imports) |
| `[tool.ruff.format]` | `quote-style` `"double"` |
| `[tool.mypy]` | `python_version` `"3.11"`, `strict` true, `files` `["src", "tests"]` |
| `[[tool.mypy.overrides]]` | one entry: `module` `["yaml", "yaml.*"]`, `ignore_missing_imports` true |
| `[tool.pytest.ini_options]` | `testpaths` `["tests"]`, `addopts` `"-q"` |

**`PRECOMMIT`** (YAML) must have a top-level `repos` list with, **in this order**:

1. `repo: https://github.com/astral-sh/ruff-pre-commit` with a `rev` like `v0.6.9`, and hooks
   `ruff` (with `args: [--fix]`) **then** `ruff-format`. Lint fixes first, so the formatter has
   the last word on layout.
2. `repo: https://github.com/pre-commit/mirrors-mypy` with a `rev` like `v1.11.2`, hook `mypy`
   with `additional_dependencies: [types-PyYAML]` (pre-commit runs mypy in its own environment,
   which needs the type stubs).
3. `repo: local` with one hook: `id: pytest`, `name: pytest`, `entry: pytest -q`,
   `language: system`, `pass_filenames: false` (run the whole suite, not one file per changed
   file), `types: [python]`.

Every `rev` must be a **string** starting with `v`.

**Example of the shape** (not the full answer):

```python
PYPROJECT = """\
[tool.ruff]
line-length = 100
"""

PRECOMMIT = """\
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
"""
```
