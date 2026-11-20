from sqlalchemy import event


class count_queries:
    def __init__(self, engine):
        self.engine = engine
        self.statements = []

    @property
    def count(self):
        return len(self.statements)

    def __enter__(self):
        # TODO: event.listen(self.engine, "before_cursor_execute", ...)
        return self

    def __exit__(self, exc_type, exc, tb):
        # TODO: event.remove(...); do not hide exceptions
        return False
