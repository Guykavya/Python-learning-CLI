# What does exit code 137 mean?

Chapter sections 4.6 (limits and restart policies) and "Try it: exit code 137". A container "dies for no reason": `docker ps -a` shows `Exited (137)`. By convention, a process that was ended by **signal n** reports the exit code **128 + n**; so 137 = 128 + 9 = `SIGKILL`, and 143 = 128 + 15 = `SIGTERM`. Write the function that turns an exit code into a sentence a person on call can act on.

## What to write

```python
SIGNALS = {1: "SIGHUP", 2: "SIGINT", 3: "SIGQUIT", 6: "SIGABRT", 9: "SIGKILL", 11: "SIGSEGV", 15: "SIGTERM"}   # given

def explain_exit(code: int) -> str: ...
```

(`SIGNALS` is given so that the answers are the same on every operating system; Windows Python does not know `SIGKILL`.)

`explain_exit` returns **exactly** these strings:

| `code` | Returns |
|---|---|
| `0` | `"0: success"` |
| `1` | `"1: the application reported a general error"` |
| `2` | `"2: usage error (bad arguments)"` |
| `126` | `"126: the command was found but could not be executed (permissions)"` |
| `127` | `"127: command not found"` |
| `129` to `192`, with `n = code - 128` in `SIGNALS` | `f"{code}: killed by signal {n} ({name})"`; but for **137** append `"; often the out-of-memory killer: check OOMKilled and the stop timeout"`, and for **143** append `"; the process was asked to stop"` |
| `129` to `192`, `n` not in `SIGNALS` | `f"{code}: killed by signal {n} (unknown name)"` |
| any other code from 3 to 255 | `f"{code}: application-specific error code"` |
| less than 0 or more than 255 | raise `ValueError` |

## Example

```python
explain_exit(0)     # '0: success'
explain_exit(137)   # '137: killed by signal 9 (SIGKILL); often the out-of-memory killer: check OOMKilled and the stop timeout'
explain_exit(143)   # '143: killed by signal 15 (SIGTERM); the process was asked to stop'
explain_exit(139)   # '139: killed by signal 11 (SIGSEGV)'
explain_exit(3)     # '3: application-specific error code'   (the chapter's crashing container exits with 3)
```
