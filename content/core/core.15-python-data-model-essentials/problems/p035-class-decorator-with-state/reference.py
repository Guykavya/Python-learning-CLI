import functools


class Recorder:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = []

    def __call__(self, *args, **kwargs):
        try:
            result = self.func(*args, **kwargs)
        except Exception as err:
            self.calls.append((args, kwargs, "error", err))
            raise
        self.calls.append((args, kwargs, "ok", result))
        return result

    @property
    def last_result(self):
        for _, _, status, value in reversed(self.calls):
            if status == "ok":
                return value
        raise LookupError("no successful call yet")

    def clear(self):
        self.calls.clear()

    def __repr__(self):
        return f"<Recorder {self.func.__name__}: {len(self.calls)} call(s)>"
