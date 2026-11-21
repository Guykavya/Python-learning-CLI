# Domain errors to HTTP, in one place

Chapter sections 4.2 (domain errors, not HTTP errors) and 4.3 (the thin route). A service raises `RuleViolation("assignee already has 3 open tasks")`; it does not know that this means HTTP 409. The **web layer** decides, and it decides **once**, in one exception handler, instead of in every route. Another caller (a command-line script) can decide that the same error means "print a message and exit 1".

## What to write

The errors are in the starter: `DomainError` and its three subclasses `NotFound`, `InvalidInput`, `RuleViolation`.

```python
def domain_error_to_http(exc) -> tuple[int, dict]: ...
def install(app) -> None: ...
```

- `domain_error_to_http(exc)` returns `(status, body)` with `body == {"detail": str(exc)}`:
  - `NotFound` (or a subclass of it) gives `404`;
  - `InvalidInput` gives `422`;
  - `RuleViolation` gives `409`;
  - any other `DomainError` gives `400`;
  - anything that is **not** a `DomainError` is not this function's business: **re-raise it** (`raise exc`), so a bug stays a bug.
  Use `isinstance`, not `type(exc) in {...}`: a project-specific subclass such as `class ProjectGone(NotFound)` must still give `404`.
- `install(app)` registers **one** exception handler on a FastAPI app, for `DomainError`, which answers with `JSONResponse(body, status_code=status)` using `domain_error_to_http`. Do not register a handler per subclass.

## Example

```python
domain_error_to_http(NotFound("project not found"))      # (404, {'detail': 'project not found'})
domain_error_to_http(RuleViolation("full"))               # (409, {'detail': 'full'})
domain_error_to_http(DomainError("something else"))       # (400, {'detail': 'something else'})
domain_error_to_http(ValueError("a bug"))                 # raises ValueError: a bug
```

After `install(app)`, a route that raises `RuleViolation("full")` answers `409 {"detail": "full"}`, and a route that raises `RuntimeError` still answers `500`.
