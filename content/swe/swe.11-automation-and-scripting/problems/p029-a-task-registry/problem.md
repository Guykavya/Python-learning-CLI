# A task registry

Chapter section 15 (structuring a personal automation suite: one command, many tasks, a registry). After a few scripts you have a folder of unrelated files, each with its own argument parsing. Give them one front door, `auto`, where adding a task is **one decorated function**, and every run goes through the job runner of p027 so it leaves a status file and an honest exit code.

## What to write

The starter gives `run_job(name, fn, status_dir)` (p027's runner: it calls `fn()`, writes `<status_dir>/<name>.json`, returns 0 or 1) and two example tasks that use your decorator. Write:

```python
TASKS = {}
def task(name): ...
def build_parser() -> argparse.ArgumentParser: ...
def main(argv=None) -> int: ...
```

- `task(name)` returns a decorator that stores the function in `TASKS[name]` and returns the function **unchanged**. Registering a name twice raises `ValueError` (two tasks silently fighting over one name is a bug).
- A task is a function `fn(args)` where `args` is the list of extra words after its name.
- `build_parser()`: `prog="auto"`, a global option `--status-dir` (default `"status"`), and subcommands:
  - `list`: prints the task names, sorted, one per line, to stdout; returns 0;
  - `run NAME [ARGS...]`: everything after `NAME` is passed to the task untouched, even words that start with `-` (use `nargs=argparse.REMAINDER` for `ARGS`).
- `main(argv)` for `run`:
  - unknown task: prints `auto: unknown task 'NAME'; known tasks: a, b` to stderr and returns **2** (a usage error);
  - otherwise returns `run_job(name, lambda: TASKS[name](extra_args), status_dir)`: `0` on success, `1` if the task raised.
- Keep the `__main__` block of the starter.

## Example

```text
$ python solution.py list
echo
hello
$ python solution.py run hello
hello from a registered task
$ python solution.py run echo a -x b
a -x b
$ python solution.py run backup; echo $?
auto: unknown task 'backup'; known tasks: echo, hello
2
```
