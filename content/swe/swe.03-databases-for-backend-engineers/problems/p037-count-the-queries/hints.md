## Hint 1

SQLAlchemy calls your function before every statement if you register it with `event.listen(engine, "before_cursor_execute", function)`. What arguments does it receive? Which one is the SQL text?

## Hint 2

Register in `__enter__` and remove in `__exit__` with `event.remove(...)`, using the **same function object**. `__exit__` runs even when the block raised.

## Hint 3

```text
class count_queries: statements = []
__enter__: event.listen(engine, "before_cursor_execute", self._record); return self
_record(self, conn, cursor, statement, parameters, context, executemany): self.statements.append(statement)
__exit__: event.remove(engine, "before_cursor_execute", self._record); return False
count = len(statements)
```
