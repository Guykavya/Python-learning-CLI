class AppError(Exception):
    status = 500

    def to_dict(self):
        return {}


class NotFound(AppError):
    def __init__(self, resource, key):
        # TODO: store the attributes and pass the message to the parent
        pass


class ValidationError(AppError):
    pass


class PermissionDenied(AppError):
    pass


def status_for(err):
    return 500


def handle(func, *args):
    return (200, func(*args))
