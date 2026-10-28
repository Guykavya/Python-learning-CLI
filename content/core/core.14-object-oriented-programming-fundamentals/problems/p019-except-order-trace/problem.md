# Trace: which except clause catches it?

Exception classes form a family tree, just like other classes. `except DbError:` catches a
`DbError` **and every subclass of it**. When an exception is raised, Python checks the `except`
clauses **from top to bottom** and runs only the **first** one that matches. Read the program and work
out what it prints.

```python
class AppError(Exception):
    pass


class DbError(AppError):
    pass


class DbTimeout(DbError):
    pass


class NetworkError(AppError):
    pass


def risky(kind):
    print("risky", kind)
    if kind == "timeout":
        raise DbTimeout("query took too long")
    if kind == "db":
        raise DbError("table missing")
    if kind == "net":
        raise NetworkError("no route")
    if kind == "value":
        raise ValueError("bad number")
    return "fine"


def handle(kind):
    try:
        result = risky(kind)
    except DbTimeout as e:
        print("timeout:", e)
    except DbError as e:
        print("db problem:", e)
    except AppError as e:
        print("app problem:", type(e).__name__, e)
    else:
        print("ok:", result)
    finally:
        print("done", kind)


for k in ["timeout", "db", "net", "none"]:
    handle(k)


def bad_order(kind):
    try:
        risky(kind)
    except AppError:
        print("caught as AppError")
    except DbTimeout:
        print("caught as DbTimeout")


bad_order("timeout")

try:
    handle("value")
except ValueError as e:
    print("outside:", e)

print(issubclass(DbTimeout, AppError), isinstance(NetworkError("x"), DbError))

try:
    risky("db")
except (NetworkError, DbTimeout):
    print("tuple caught")
except Exception as e:
    print("generic:", type(e).__name__)
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- The family tree is: `AppError` → `DbError` → `DbTimeout`, and `AppError` → `NetworkError`.
  All of them come from `Exception`. `ValueError` is not part of this family.
- `print(e)` or `print("x:", e)` shows the exception's message, for example `query took too long`.
- `type(e).__name__` is the class name as text, for example `NetworkError`.
- `else:` runs only if the `try` block raised **nothing**. `finally:` always runs, even when the
  exception is not caught and keeps going up to the caller.
- `except (A, B):` matches if the exception is an `A` or a `B` (or a subclass of either).

## Example of the format

```python
try:
    raise DbTimeout("slow")
except AppError as e:
    print("got", type(e).__name__, e)
```

prints

```text
got DbTimeout slow
```
