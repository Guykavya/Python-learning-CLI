## Hint 1

`tomllib.loads(text)` gives a nested dictionary. Which keys do you read, and what do you do when one is absent (`dict.get` with a default)?

## Hint 2

For `testpaths`: an entry such as `"tests"` counts as present when some file path starts with `"tests/"`. For the package: a regular expression like `src/[^/]+/__init__\.py` against every file. For the version bound: one regex looking for an operator followed by a digit.

## Hint 3

```text
parse; on TOMLDecodeError return ["invalid TOML"]
problems = []
check project.name / version (or dynamic) / requires-python
check the src package
for each testpaths entry: folder missing?
ruff twice?
deps = dependencies + every optional-dependencies group
for each dep: no (>=|==|~=|===|>)\s*\d  -> problem
```
