from fastapi.responses import JSONResponse


class DomainError(Exception):
    """A business rule was broken. This is a normal outcome, not a bug."""


class NotFound(DomainError):
    pass


class InvalidInput(DomainError):
    pass


class RuleViolation(DomainError):
    pass


def domain_error_to_http(exc):
    if not isinstance(exc, DomainError):
        raise exc                                   # a bug is not a business outcome
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
