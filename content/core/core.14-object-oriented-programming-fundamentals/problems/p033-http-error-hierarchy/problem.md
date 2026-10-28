# An error hierarchy for a web app

A web app must answer every request with an HTTP status code: 404 when something does not exist,
422 when the input is wrong, 403 when the user is not allowed, and 500 when the program itself
broke. Give the app its own exception classes, so the code that sends the answer can catch **one**
base class and still send the right code. Write it in `solution.py`.

**Exception classes**

- `AppError(Exception)`: the base. Class attribute `status = 500`. `AppError(message)` stores the
  message so that `str(err)` gives it. Method `to_dict()` returns
  `{"error": <class name>, "message": str(self), "status": self.status}`.
- `NotFound(AppError)`: `status = 404`. `NotFound(resource, key)`; attributes `resource`, `key`;
  message `f"{resource} {key!r} not found"`.
- `ValidationError(AppError)`: `status = 422`. `ValidationError(field, problem)`; attributes
  `field`, `problem`; message `f"{field}: {problem}"`.
- `PermissionDenied(AppError)`: `status = 403`. `PermissionDenied(user, action)`; attributes
  `user`, `action`; message `f"{user} may not {action}"`.

Each subclass must pass its message to the parent with `super().__init__(message)`.

**Functions**

- `status_for(err)` returns the status for any exception: `err.status` for an `AppError` (also for
  subclasses that someone writes later), and `500` for every other exception.
- `handle(func, *args)` calls `func(*args)` and returns a pair `(status, body)`:
  - success: `(200, result)`;
  - an `AppError`: `(err.status, err.to_dict())`;
  - any other `Exception`: `(500, {"error": "InternalError", "message": "internal server error", "status": 500})`.
    Do not show the real message: it may contain secrets.

**Example**

```python
err = NotFound("book", 42)
str(err)               # 'book 42 not found'
err.status             # 404
isinstance(err, AppError)   # True
status_for(ValidationError("email", "missing @"))   # 422
status_for(KeyError("x"))                           # 500

def get_book(book_id):
    if book_id != 1:
        raise NotFound("book", book_id)
    return {"id": 1, "title": "Python"}

handle(get_book, 1)    # (200, {'id': 1, 'title': 'Python'})
handle(get_book, 7)    # (404, {'error': 'NotFound', 'message': 'book 7 not found', 'status': 404})
```
