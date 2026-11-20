# Check a `pyproject.toml`

A reviewer (or a CI job) can check a project's setup automatically. Write

```python
check_pyproject(text, files)
```

`text` is the content of `pyproject.toml`, parsed with `tomllib` (standard library, Python 3.11+). `files` is the list of file paths in the repository, relative, with `/` (for example `["src/pricekit/__init__.py", "tests/test_core.py"]`).

Return a **list of problem messages**, in this order, each one only when it applies:

| Message | When |
|---|---|
| `"invalid TOML"` | the text does not parse (then return only this one) |
| `"missing project.name"` | no `[project] name` |
| `"missing project.version"` | no `version`, and `"version"` is not in `dynamic` |
| `"missing project.requires-python"` | no `requires-python` |
| `"no package under src/"` | no file matches `src/<package>/__init__.py` |
| `"testpaths folder missing: <entry>"` | an entry of `[tool.pytest.ini_options] testpaths` has no file under it (one message per entry) |
| `"ruff is configured twice (pyproject.toml and ruff.toml)"` | `[tool.ruff]` exists in the pyproject **and** `ruff.toml` or `.ruff.toml` is among the files |
| `"dependency without a lower bound: <dep>"` | a dependency in `dependencies` or in any `optional-dependencies` group has no `>=`, `==`, `~=`, `===` or `>` followed by a version (one message per dependency, in the order found) |

A correct project gives `[]`: the `pyproject.toml` of chapter section 17.4 with the files of the template is the model.

## Example

```python
check_pyproject('[project]\nname = "x"\n', ["x.py"])
# ["missing project.version", "missing project.requires-python", "no package under src/"]
```
