## Hint 1

`subprocess.run` raises `subprocess.TimeoutExpired` when the timeout passes (after killing the
child). Where do you put the `try` / `except`, and what do you return from the `except` block?
Outside it, how do you turn `proc.returncode` into `"ok"` or `"failed"`?

## Hint 2

`describe_exit` is a chain of `if`s: check `None` first (because `None > 0` raises
`TypeError`), then `0`, then positive, then negative. For `first_success`, `enumerate` gives the
index; `return` inside the loop stops it at the first success.

## Hint 3

```
run_limited:
    try:
        proc = run([sys.executable, "-c", code], stdin=DEVNULL, capture_output=True,
                   text=True, encoding="utf-8", timeout=timeout)
    except TimeoutExpired:
        return "timeout", None, ""
    return ("ok" if proc.returncode == 0 else "failed"), proc.returncode, proc.stdout

first_success:
    for i, code in enumerate(snippets):
        if run_limited(code, timeout)[0] == "ok": return i
    return -1
```
