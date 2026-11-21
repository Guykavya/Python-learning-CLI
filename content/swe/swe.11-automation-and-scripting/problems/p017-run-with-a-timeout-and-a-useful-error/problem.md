# Run with a timeout and a useful error

Chapter section 7.1 (the safe way: `check=True`, `capture_output`, always a `timeout`) and 13.4 (every subprocess has a timeout). When a scheduled job calls `pg_dump` or `git` and it fails at 3 a.m., the log line is all you get. "Command failed" is useless; "`git pull` failed with exit code 128: fatal: could not read from remote repository" tells you what to fix.

## What to write

```python
class ToolFailed(Exception):
    def __init__(self, command, code, stderr_tail, message): ...

def run_tool(args, timeout) -> str: ...
```

`ToolFailed` keeps three attributes besides its message: `command` (the list of arguments), `code` (the exit code, or `None` when there was none), and `stderr_tail` (a list with at most the **last 5 lines** of the child's stderr).

`run_tool(args, timeout)` runs `args` (a list) with `capture_output=True, text=True, check=True, timeout=timeout` and returns the child's **stdout** on success. Every failure becomes a `ToolFailed`:

| What happened | `code` | Message starts with |
|---|---|---|
| exit code not 0 (`CalledProcessError`) | the exit code | `<command> failed with exit code <code>` |
| too slow (`TimeoutExpired`) | `None` | `<command> timed out after <timeout>s` |
| program not found (`FileNotFoundError`) | `None` | `<command> could not start` |

`<command>` is the arguments joined with spaces. If there is a stderr tail, the message continues with a newline and the tail lines joined by newlines, so the log shows the reason. Raise with `from e`, so the original exception stays in the traceback.

Note: when a timeout happens, `TimeoutExpired.stderr` may be `None` or **bytes** even with `text=True`; handle both.

## Example

```python
run_tool([sys.executable, "-c", "print('hi')"], timeout=10)          # 'hi\n'
try:
    run_tool(["git", "pull"], timeout=60)
except ToolFailed as e:
    print(e)
# git pull failed with exit code 128
# fatal: could not read from remote repository.
e.code, e.stderr_tail      # (128, ['fatal: could not read from remote repository.'])
```
