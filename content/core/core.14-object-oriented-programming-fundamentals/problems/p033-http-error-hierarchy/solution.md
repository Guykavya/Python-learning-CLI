## Approach

**One base class for the library.** Every error the app raises on purpose inherits from `AppError`
(chapter section 17). Callers who do not care about details write one `except AppError`. Callers
who do care catch `NotFound` alone. A bug like a `KeyError` stays outside the family and is
treated as an internal error.

**Data on the exception.** Each subclass takes the facts it needs (`resource`, `key`, ...),
stores them as attributes so code can read them, and builds a readable message for humans. It
passes the message to `super().__init__`, because `Exception` is what makes `str(err)` work.

**The status is a class attribute.** `status_for` does not need a table of classes; `err.status`
finds the right number through normal attribute lookup, including in subclasses written later
(`Gone` with 410, or `MissingPage` inheriting 404). Adding a new error never changes
`status_for`. That is polymorphism with data instead of methods.

**`handle`: specific before general.** `except AppError` comes first. If `except Exception` came
first, it would catch the `NotFound` too and every error would become a 500. `except Exception`
(never a bare `except:`) leaves `KeyboardInterrupt` alone, so Ctrl+C still stops the server.

## Code

```python
class AppError(Exception):
    """Base class for every error this app raises on purpose."""

    status = 500

    def __init__(self, message):
        super().__init__(message)

    def to_dict(self):
        return {"error": type(self).__name__, "message": str(self), "status": self.status}


class NotFound(AppError):
    status = 404

    def __init__(self, resource, key):
        self.resource = resource
        self.key = key
        super().__init__(f"{resource} {key!r} not found")


class ValidationError(AppError):
    status = 422

    def __init__(self, field, problem):
        self.field = field
        self.problem = problem
        super().__init__(f"{field}: {problem}")


class PermissionDenied(AppError):
    status = 403

    def __init__(self, user, action):
        self.user = user
        self.action = action
        super().__init__(f"{user} may not {action}")


def status_for(err):
    if isinstance(err, AppError):
        return err.status
    return 500


INTERNAL = {"error": "InternalError", "message": "internal server error", "status": 500}


def handle(func, *args):
    try:
        result = func(*args)
    except AppError as err:
        return err.status, err.to_dict()
    except Exception:
        return 500, dict(INTERNAL)
    return 200, result
```

`dict(INTERNAL)` returns a copy, so a caller that changes the body cannot change the shared constant.
The `try` block contains only the call; the success `return` sits after it, so an error in our own
code is not mistaken for an error in `func`.

## Complexity

All O(1).

## Another way

`status_for` could also be written with `getattr(err, "status", 500)`. That is shorter, but any
exception that happens to have a `status` attribute (some libraries' errors do) would leak its own
number into your app. The `isinstance(err, AppError)` check keeps the rule exact. A real web
framework also logs the hidden internal error (with its traceback) before sending the 500.
