# Timeouts and exit codes

A program that starts other programs must expect them to fail, and to hang. Two tools:

- **Exit codes.** `proc.returncode` is `0` for success and a positive number for an error chosen by
  the program (`sys.exit(2)` gives 2; an uncaught exception or `sys.exit("message")` gives 1).
  On Linux and macOS a **negative** code `-N` means the child was killed by signal `N`.
- **Timeouts.** `subprocess.run(..., timeout=seconds)` kills the child when time runs out and
  raises `subprocess.TimeoutExpired`. Without a timeout, one stuck child blocks your program forever.

As before, every child is `[sys.executable, "-c", code]`. Giving it an empty stdin
(`stdin=subprocess.DEVNULL`) is good practice too, so it can never wait for the keyboard.

Write in `solution.py`:

1. `run_limited(code, timeout) -> tuple[str, int | None, str]`: run the child for at most `timeout`
   seconds. Return `("ok", 0, stdout)` on exit code 0, `("failed", returncode, stdout)` on any
   other exit code, or `("timeout", None, "")` if it was stopped by the timeout. It must never raise.
2. `describe_exit(returncode) -> str`: `None` -> `"timed out"`, `0` -> `"success"`, positive `n` ->
   `"error (exit code n)"`, negative `-n` -> `"killed by signal n"`.
3. `first_success(snippets, timeout) -> int`: run the snippets in order and return the index of
   the first one whose status is `"ok"`; `-1` if none. Do **not** run the snippets after the first success.

The tests use a child that sleeps for 10 seconds with `timeout=0.5`, so a correct solution
finishes in about a second; a missing timeout makes the tests take 10 seconds or more and fail.

**Example**

```python
run_limited("print('hi')", 5)                       # ('ok', 0, 'hi\n')
run_limited("import sys; sys.exit(2)", 5)           # ('failed', 2, '')
run_limited("import time; time.sleep(10)", 0.5)     # ('timeout', None, '')
describe_exit(-9)                                   # 'killed by signal 9'
first_success(["1/0", "print('ok')", "print('never run')"], 5)   # 1
```
