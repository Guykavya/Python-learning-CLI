## Approach

The safe way to run a program is to describe the command as a **list**: the program first, then one
item per argument. `subprocess.run` then starts the program directly (no shell), and the operating
system hands each item over as one argument. Characters such as space, `;`, `&`, `|`, `$( )`, `>`,
quotes or `%` are just characters: nothing interprets them.

`sys.executable` is the full path of the running Python, so the helper runs in the same interpreter and
virtual environment. Checking that every argument is a `str` catches mistakes early (an `int` in the
list would fail later with a less clear message).

`check=True` turns a non-zero exit code into `CalledProcessError`, and `timeout` turns a stuck helper
into `TimeoutExpired`: failures become exceptions instead of silent empty output.

## Code

```python
import subprocess
import sys


def build_command(script, args):
    for arg in args:
        if not isinstance(arg, str):
            raise TypeError(f"every argument must be a str, got {arg!r}")
    return [sys.executable, str(script), *args]


def run_script(script, args, timeout=10.0):
    cmd = build_command(script, args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=timeout,
    )
    return result.stdout
```

## Complexity

O(n) to build the list for n arguments; running the program costs whatever the program costs
(starting a Python process takes tens of milliseconds).

## Another way

If you really need a shell feature (a pipe, a glob) on Linux, quote **every** piece with
`shlex.quote` (or build the string with `shlex.join(list)`) before `shell=True`. That quoting is for
POSIX shells only and does not protect you on Windows, so the list form is still the better default:
do the "shell work" in Python instead (`pathlib.Path.glob` for `*.py`, two `subprocess.run` calls and
`input=` for a pipe).
