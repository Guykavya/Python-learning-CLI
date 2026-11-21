## Approach

```python
def domain_error_to_http(exc):
    if not isinstance(exc, DomainError):
        raise exc
    if isinstance(exc, NotFound):
        status = 404
    elif isinstance(exc, InvalidInput):
        status = 422
    elif isinstance(exc, RuleViolation):
        status = 409
    else:
        status = 400
    return status, {"detail": str(exc)}


def install(app):
    @app.exception_handler(DomainError)
    def handle(request, exc):
        status, body = domain_error_to_http(exc)
        return JSONResponse(body, status_code=status)
```

Splitting the **decision** (`domain_error_to_http`, a pure function you can test with no web server) from the **registration** (`install`) is what makes the translation testable and keeps it in one place: a new error type is one new line here, never a change in a route.

## Complexity

O(1) per error.

## Another way

The chapter's version looks the status up with `STATUS_FOR.get(type(exc), 400)`. That is shorter but exact-type: `ProjectGone(NotFound)` would silently become a 400. A loop over the dictionary with `isinstance` keeps the table and fixes the subclass case: `next((s for cls, s in STATUS_FOR.items() if isinstance(exc, cls)), 400)`.
