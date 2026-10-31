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
