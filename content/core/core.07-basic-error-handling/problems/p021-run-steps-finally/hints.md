## Hint 1

Which of the four clauses `try`, `except`, `else`, `finally` matches each of the log lines
"done", "failed" and "end"?

## Hint 2

If a step raises `KeyError`, no `except` clause matches. What still runs before the exception
leaves the function?

## Hint 3

```
log start
try: func()
except ValueError as e: log failed with e
else: log done; count it
finally: log end
```
