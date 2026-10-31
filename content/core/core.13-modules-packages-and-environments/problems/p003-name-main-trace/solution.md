## Approach

Before running a file, Python creates a module object and sets its `__name__`.

- The file given to `python file.py` runs as the **main program**, so its `__name__` is `"__main__"`.
- A file that is **imported** gets its module name: `tools` or `app`.

**Command 1.** `app.py` is the main program: it prints `__main__`. Then `import tools` runs `tools.py`,
whose `__name__` is `tools`, so its `if` block is skipped. Back in `app`, `shout("hi")` gives `HI!`, and
the `if` in `app.py` is true.

**Command 2.** Now `tools.py` is the main program: `__name__` is `__main__`, and the `if` block runs.

**Command 3.** The `-c` string is the main program. It imports `app`, so `app.py` runs with
`__name__ == "app"`; it imports `tools` as before. Neither `if` block runs.

## Output

```text
app: __name__ is __main__
tools: __name__ is tools
HI!
tools.__name__ = tools
app running as a script
---
tools: __name__ is __main__
tools running as a script
DEMO!
---
app: __name__ is app
tools: __name__ is tools
HI!
tools.__name__ = tools
```

## Complexity

O(1).

## Another way

Run `python -m tools`. The `-m` switch finds the module on `sys.path` and runs it as `__main__`, so the
output is the same as command 2.
