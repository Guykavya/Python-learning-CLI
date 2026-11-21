## Hint 1

Three different exceptions can come out of `subprocess.run` here. Catch each one separately, because each knows different things: `CalledProcessError` has `.returncode` and `.stderr`; `TimeoutExpired` has `.timeout` and maybe `.stderr` (as bytes or `None`); `FileNotFoundError` has neither. How do you take the last 5 items of a list that might be shorter than 5?

## Hint 2

```text
def tail(text):
    if text is None: return []
    if bytes: decode("utf-8", errors="replace")
    return text.splitlines()[-5:]
command = " ".join(str(a) for a in args)
try: return subprocess.run(args, capture_output=True, text=True, check=True, timeout=timeout).stdout
except CalledProcessError as e: raise ToolFailed(args, e.returncode, tail(e.stderr), f"{command} failed with exit code {e.returncode}") from e
except TimeoutExpired as e:     raise ToolFailed(args, None, tail(e.stderr), f"{command} timed out after {timeout}s") from e
except FileNotFoundError as e:  raise ToolFailed(args, None, [], f"{command} could not start: {e}") from e
(ToolFailed.__init__ appends "\n" + the tail lines to the message when there is a tail)
```
