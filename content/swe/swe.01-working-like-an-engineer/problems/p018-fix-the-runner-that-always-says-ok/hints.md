## Hint 1

Read `main` and ask three questions: what does it do with the **value** returned by `run`? Which interpreter does `PY` name? In which order does `check` list its parts?

## Hint 2

One bug is in the line `run(cmd)`, one in the first line `PY = ...`, and one in the line that builds `TASKS["check"]`.

## Hint 3

```text
PY = [sys.executable, "-m"]
for cmd in ...:
    code = run(cmd)
    if code != 0: return code
TASKS["check"] = lint + types + test
```
