## Hint 1

Follow `import bank` step by step. `__init__.py` starts `accounts`. Its first line starts `audit`.
`audit`'s first line asks the half-built `accounts` for `balance`. How far has `accounts` got at that
moment? Which of the two modules needs the other **while it loads**, and which only needs it later,
inside a function?

## Hint 2

`accounts` calls `log` in many functions; `audit` uses `balance` only inside `report`. So `audit`
is the one that can wait:

```text
audit.py:
    (no import of accounts at the top)
    _entries = []
    def log(...), def history(...) as before
    def report(name):
        from .accounts import balance     # runs at call time; accounts is complete by then
        ...same body...
```

Python caches the module after the first import, so the import inside `report` is cheap.
