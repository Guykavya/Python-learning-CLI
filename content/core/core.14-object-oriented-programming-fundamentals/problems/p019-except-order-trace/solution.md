## Approach

The first matching `except` wins, and "matching" means `isinstance(exception, ThatClass)` (chapter
section 17).

1. `handle("timeout")`: `risky timeout`; `DbTimeout` matches the first clause → `timeout: query took
   too long`; `done timeout`.
2. `handle("db")`: a `DbError` is not a `DbTimeout`, so the first clause is skipped; the second
   matches → `db problem: table missing`; `done db`.
3. `handle("net")`: `NetworkError` is neither a `DbTimeout` nor a `DbError`, but it is an `AppError`
   → `app problem: NetworkError no route`; `done net`.
4. `handle("none")`: nothing raised → `else` → `ok: fine`; `done none`.
5. `bad_order("timeout")`: `except AppError` comes first and already matches a `DbTimeout` →
   `caught as AppError`. The `DbTimeout` clause can **never** run; it is dead code.
6. `handle("value")`: `ValueError` matches no clause. `finally` still prints `done value`, then the
   error leaves `handle` and the outer `try` prints `outside: bad number`.
7. `DbTimeout` is a subclass of `AppError` → `True`. A `NetworkError` is not a `DbError` → `False`.
8. `risky("db")` raises `DbError`. It is not a `NetworkError` and not a `DbTimeout` (a parent is not
   an instance of its child), so the tuple does not match; `except Exception` does → `generic: DbError`.

## Output

```text
risky timeout
timeout: query took too long
done timeout
risky db
db problem: table missing
done db
risky net
app problem: NetworkError no route
done net
risky none
ok: fine
done none
risky timeout
caught as AppError
risky value
done value
outside: bad number
True False
risky db
generic: DbError
```

## Complexity

Not applicable.

## Another way

Rule of thumb: order `except` clauses from the most specific class to the most general, like the
`isinstance` checks in p013. Linters such as `pylint` warn about a clause that can never be reached,
like the `DbTimeout` clause in `bad_order`.
