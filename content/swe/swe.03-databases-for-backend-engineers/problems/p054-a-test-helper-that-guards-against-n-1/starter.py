from sqlalchemy import event


class assert_max_queries:
    def __init__(self, engine, n):
        self.engine = engine
        self.n = n
        self.statements = []

    def __enter__(self):
        # TODO: listen to before_cursor_execute and record the statements
        return self

    def __exit__(self, exc_type, exc, tb):
        # TODO: remove the listener; if the block succeeded and too many ran, raise AssertionError listing them
        return False
