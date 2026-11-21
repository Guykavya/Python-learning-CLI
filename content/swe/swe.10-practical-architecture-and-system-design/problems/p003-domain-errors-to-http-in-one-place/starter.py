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
    # TODO: (status, {"detail": str(exc)}); re-raise anything that is not a DomainError
    return 500, {}


def install(app):
    # TODO: ONE handler for DomainError
    pass
