## Hint 1

Which check decides "this is a business outcome" and which is "this is a bug"? Do that check first, and for the bug do nothing clever: raise it again. For the status codes, in which order must you test `isinstance` if some classes could be subclasses of others?

## Hint 2

```text
domain_error_to_http(exc):
    if not isinstance(exc, DomainError): raise exc
    NotFound -> 404; InvalidInput -> 422; RuleViolation -> 409; otherwise 400
    return status, {"detail": str(exc)}
install(app): @app.exception_handler(DomainError) def handle(request, exc): status, body = domain_error_to_http(exc); return JSONResponse(body, status_code=status)
```
