## Hint 1

In TOML, `[a.b]` opens the table `b` inside `a`, and `[[a.b]]` adds **one item to a list** of
tables called `b`. Which of the settings above is a list of tables? In YAML, a `-` starts a list
item and indentation shows nesting: what is the nesting from `repos` down to one hook's `id`?

## Hint 2

Build it piece by piece and check each piece in the REPL with
`tomllib.loads(PYPROJECT)["tool"]["ruff"]` and `yaml.safe_load(PRECOMMIT)["repos"][0]`.

```
[tool.ruff.lint]
select = [...six strings...]
...
[[tool.mypy.overrides]]
module = [...]
ignore_missing_imports = true

repos:
  - repo: ...
    rev: v...
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  ...
  - repo: local
    hooks:
      - id: pytest
        pass_filenames: false
```
