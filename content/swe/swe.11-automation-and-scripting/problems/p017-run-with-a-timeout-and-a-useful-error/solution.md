## Approach

```python
class ToolFailed(Exception):
    def __init__(self, command, code, stderr_tail, message):
        self.command, self.code, self.stderr_tail = command, code, stderr_tail
        if stderr_tail:
            message = message + "\n" + "\n".join(stderr_tail)
        super().__init__(message)


def _tail(text, n=5):
    if text is None:
        return []
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    return text.splitlines()[-n:]


def run_tool(args, timeout):
    command = " ".join(str(a) for a in args)
    try:
        return subprocess.run(args, capture_output=True, text=True, check=True, timeout=timeout).stdout
    except subprocess.CalledProcessError as e:
        raise ToolFailed(args, e.returncode, _tail(e.stderr), f"{command} failed with exit code {e.returncode}") from e
    except subprocess.TimeoutExpired as e:
        raise ToolFailed(args, None, _tail(e.stderr), f"{command} timed out after {timeout}s") from e
    except FileNotFoundError as e:
        raise ToolFailed(args, None, [], f"{command} could not start: {e}") from e
```

One exception type for the caller (`ToolFailed`), with the three facts an operator needs: **what** ran, **how** it ended, and the **last words** of the tool. The last lines are where tools print the reason; the first lines are usually progress. `from e` keeps the original exception chained for debugging.

## Complexity

The cost of the child process; the tail is O(stderr size).

## Another way

Stream stderr to your own log while the child runs (`Popen` and read line by line, section 7.2), keeping only a `collections.deque(maxlen=5)` of the last lines. That gives live progress in the log *and* the tail in the error, and it never holds megabytes of output in memory.
