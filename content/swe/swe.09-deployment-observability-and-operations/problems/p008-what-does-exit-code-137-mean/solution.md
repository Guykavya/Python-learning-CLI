## Approach

```python
def explain_exit(code):
    if not 0 <= code <= 255:
        raise ValueError(f"an exit code is between 0 and 255, got {code}")
    if code in FIXED:
        return FIXED[code]
    if 129 <= code <= 192:
        n = code - 128
        text = f"{code}: killed by signal {n} ({SIGNALS.get(n, 'unknown name')})"
        if code == 137:
            text += "; often the out-of-memory killer: check OOMKilled and the stop timeout"
        elif code == 143:
            text += "; the process was asked to stop"
        return text
    return f"{code}: application-specific error code"
```

The convention "128 + n" is why `Exited (137)` means `SIGKILL`. The chapter shows two causes (4.6 and the "Try it"): the kernel's out-of-memory killer (`docker inspect` says `OOMKilled=true`), or something sending `SIGKILL`: `docker kill`, or a `docker stop` whose grace period ran out because the process ignored `SIGTERM` (p002).

## Complexity

O(1).

## Another way

On Linux and macOS, `signal.Signals(n).name` gives the name for any valid `n` (and raises `ValueError` otherwise). It is not used here because the set of signals differs between operating systems, and a test that passes on Linux must pass on Windows too.
