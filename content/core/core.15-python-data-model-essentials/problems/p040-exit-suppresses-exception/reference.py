class Ignore:
    def __init__(self, *exc_types):
        self.exc_types = exc_types
        self.exception = None

    def __enter__(self):
        self.exception = None
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None and issubclass(exc_type, self.exc_types):
            self.exception = exc
            return True
        return False

    @property
    def caught(self):
        return self.exception is not None


class Expect:
    def __init__(self, exc_type):
        self.exc_type = exc_type
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            raise AssertionError(f"expected {self.exc_type.__name__}, but nothing was raised")
        if issubclass(exc_type, self.exc_type):
            self.exception = exc
            return True
        return False
