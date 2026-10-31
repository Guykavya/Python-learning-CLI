## Approach

`timeout=` turns "might hang forever" into an exception you can handle. `subprocess.run` kills
the child and waits for it to be gone before raising `TimeoutExpired`, so no stray process is
left behind. Catch exactly that exception and report it as data (`"timeout"`), like the other
outcomes.

Exit codes are the child's way of reporting: `0` success, positive numbers are the program's own
error codes, and on POSIX systems a negative value means a signal ended it (`-9` is `SIGKILL`,
`-15` is `SIGTERM`). `sys.exit("message")` prints the message to stderr and exits with 1; an
uncaught exception also gives 1.

`first_success` returns from inside the loop, so later snippets are never started. That matters
when running them has side effects (here: creating a file) or costs time.

## Code

```python
import subprocess
import sys


def run_limited(code: str, timeout: float) -> tuple[str, int | None, str]:
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return "timeout", None, ""
    status = "ok" if proc.returncode == 0 else "failed"
    return status, proc.returncode, proc.stdout


def describe_exit(returncode: int | None) -> str:
    if returncode is None:
        return "timed out"
    if returncode == 0:
        return "success"
    if returncode > 0:
        return f"error (exit code {returncode})"
    return f"killed by signal {-returncode}"


def first_success(snippets: list[str], timeout: float) -> int:
    for index, code in enumerate(snippets):
        status, _, _ = run_limited(code, timeout)
        if status == "ok":
            return index
    return -1
```

## Complexity

Each child costs one process start plus its own run time, capped by `timeout`. `first_success`
runs at most `len(snippets)` children and at most `len(snippets) * timeout` seconds.

## Another way

`TimeoutExpired` carries the output produced before the timeout in `e.stdout` (bytes or `None`,
depending on the platform), so you could return the partial output instead of `""`. With
`subprocess.Popen` you control the waiting yourself: `proc.wait(timeout=...)`, then `proc.kill()`
and `proc.wait()` again, which is what `run` does for you. On POSIX, `signal.Signals(9).name`
turns a signal number into a name such as `'SIGKILL'`.
