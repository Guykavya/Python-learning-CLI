CALL_LOG = []


def logged(func):
    # TODO: wrap func: append "name(args)" to CALL_LOG, then call it
    return func


def logged_as(prefix):
    # TODO: a decorator factory; the log string starts with "prefix: "
    def decorator(func):
        return func

    return decorator
