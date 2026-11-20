# A pure-Python task runner

Chapter sections 13.4 and 17.5 build `tasks.py`: one file that runs `test`, `lint`, `types` and `check`. To make it **testable**, the function that actually starts a program is passed in:

```python
main(argv, run)
```

- `argv` is like `sys.argv`: `["tasks.py", "test"]`.
- `run(cmd)` runs a command (a list of strings) and returns its **exit code**. The tests pass a fake `run` that records the commands.
- `main` returns the exit code of the program.

| Task | Commands, in order |
|---|---|
| `test` | `[sys.executable, "-m", "pytest"]` |
| `lint` | `[sys.executable, "-m", "ruff", "check", "."]`, then `[sys.executable, "-m", "ruff", "format", "--check", "."]` |
| `types` | `[sys.executable, "-m", "mypy"]` |
| `check` | all of `lint`, then `types`, then `test` |

Rules:

1. Stop at the **first command that fails** (exit code not 0) and return **that code**; later commands are not run.
2. Commands start with `sys.executable` (the Python that is running you, so it is the right virtual environment), never the word `"python"`.
3. With no task or an unknown task: print a usage text and return `2`. The usage text is the line `usage: python tasks.py <task>` followed by one line per task (`  test   run the tests`, and so on), and the command is not run.
4. On success return `0`.

## Example

```python
calls = []
def run(cmd):
    calls.append(cmd)
    return 0

main(["tasks.py", "types"], run)     # 0
calls                                 # [[sys.executable, "-m", "mypy"]]
```
