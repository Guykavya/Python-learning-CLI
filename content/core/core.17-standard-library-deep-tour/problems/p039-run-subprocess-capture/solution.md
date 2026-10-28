## Approach

`subprocess.run` with a **list** starts the program directly; there is no shell, so nothing is
interpreted: spaces, quotes, `;`, `$` and `*` in an argument reach the child exactly as written
(the `echo_args` tests prove it). The keyword arguments each fix one problem:

- `capture_output=True` collects stdout and stderr (separately) instead of letting them go to the terminal.
- `text=True` (with `encoding="utf-8"`) decodes the bytes to `str` and turns Windows `\r\n` into `\n`.
- `input=stdin_text` sends text to the child's stdin and then closes it, so a child that reads
  stdin gets end-of-file instead of waiting for the keyboard.
- `timeout=` kills the child and raises `TimeoutExpired` if it takes too long (next problem).

A non-zero exit code is information, not an exception: `run_python` returns it, and
`run_or_raise` turns it into a short, useful error message. `check=True` in `echo_args` raises
`CalledProcessError` if that tiny child ever fails.

## Code

```python
import json
import subprocess
import sys

TIMEOUT = 10


def run_python(code: str, stdin_text: str = "") -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, "-c", code],
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=TIMEOUT,
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_or_raise(code: str) -> str:
    returncode, out, err = run_python(code)
    if returncode != 0:
        lines = [line for line in err.splitlines() if line.strip()]
        raise RuntimeError(lines[-1] if lines else f"exit code {returncode}")
    return out


def echo_args(args: list[str]) -> list[str]:
    code = "import json, sys; print(json.dumps(sys.argv[1:]))"
    proc = subprocess.run(
        [sys.executable, "-c", code, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=TIMEOUT,
        check=True,
    )
    return json.loads(proc.stdout)
```

## Complexity

Starting a Python process costs tens of milliseconds; that dominates everything else here. The
output is held in memory, so this style suits programs with modest output.

## Another way

`subprocess.run(..., check=True)` raises `CalledProcessError` (with `.returncode`, `.stdout` and
`.stderr` attributes) for a non-zero exit, which you could catch and convert in `run_or_raise`.
For a child that produces a lot of output, or that you talk to while it runs, use
`subprocess.Popen` and read from `proc.stdout` line by line instead of capturing everything.
