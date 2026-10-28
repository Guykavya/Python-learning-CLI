## Approach

Splitting a command line correctly is harder than it looks (quotes, escapes, comments), and
quoting is where security bugs live: an argument like `x; rm -rf ~` joined with plain spaces and
given to a shell runs a second command. `shlex` implements the POSIX rules for both directions,
so the code is one call each.

For the settings line, the shell-style split does the hard part (quoted values with spaces,
comments); then `partition("=")` cuts at the first `=` only, so values may contain `=`.

## Code

```python
import shlex


def split_command(line: str) -> list[str]:
    return shlex.split(line, comments=True)


def join_command(args: list[str]) -> str:
    return shlex.join(args)


def parse_settings(line: str) -> dict[str, str]:
    settings = {}
    for token in shlex.split(line, comments=True):
        key, sep, value = token.partition("=")
        if not sep or not key:
            raise ValueError(f"expected key=value, got {token!r}")
        settings[key] = value
    return settings
```

## Complexity

O(n) in the length of the line for each function.

## Another way

`" ".join(shlex.quote(a) for a in args)` is exactly what `shlex.join` does (it was added in
Python 3.8). For real programs that run commands, you rarely need either: pass a **list** to
`subprocess.run([...])` and no shell is involved, so nothing needs quoting. `shlex.split` is still
useful to turn a command that a user typed (or wrote in a config file) into such a list.
