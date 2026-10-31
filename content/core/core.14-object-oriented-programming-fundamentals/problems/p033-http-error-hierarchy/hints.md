## Hint 1

Where should the number 404 live? If it is a class attribute of `NotFound`, then `err.status` finds
it for every `NotFound` object, and a subclass can override it. So does `status_for` need one
`isinstance` check per class, or only one check for `AppError`?

## Hint 2

A subclass `__init__` takes other arguments (`resource, key`), builds the message text, and passes
it up: `super().__init__(message)`. `Exception` stores it, and `str(err)` returns it. Without that
call, `str(err)` is wrong. In `handle`, the order of the `except` clauses matters: which one must
come first, `except AppError` or `except Exception`?

## Hint 3

```
class NotFound(AppError):
    status = 404
    __init__(resource, key):
        self.resource = resource; self.key = key
        super().__init__(f"{resource} {key!r} not found")

status_for(err):
    return err.status if isinstance(err, AppError) else 500

handle(func, *args):
    try: result = func(*args)
    except AppError as err: return err.status, err.to_dict()
    except Exception:       return 500, {...internal...}
    return 200, result
```
