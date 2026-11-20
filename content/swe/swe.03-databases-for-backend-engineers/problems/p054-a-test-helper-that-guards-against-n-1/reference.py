from sqlalchemy import event


class assert_max_queries:
    def __init__(self, engine, n):
        self.engine = engine
        self.n = n
        self.statements = []

    def _record(self, conn, cursor, statement, parameters, context, executemany):
        self.statements.append(statement)

    def __enter__(self):
        event.listen(self.engine, "before_cursor_execute", self._record)
        return self

    def __exit__(self, exc_type, exc, tb):
        event.remove(self.engine, "before_cursor_execute", self._record)
        if exc_type is None and len(self.statements) > self.n:
            lines = "\n".join(f"  {i}. {s}" for i, s in enumerate(self.statements, 1))
            raise AssertionError(f"expected at most {self.n} queries, but {len(self.statements)} ran:\n{lines}")
        return False
