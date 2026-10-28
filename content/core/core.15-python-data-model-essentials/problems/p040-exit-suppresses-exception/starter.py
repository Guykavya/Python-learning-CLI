class Ignore:
    def __init__(self, *exc_types):
        self.exc_types = exc_types
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class Expect:
    def __init__(self, exc_type):
        self.exc_type = exc_type
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False
