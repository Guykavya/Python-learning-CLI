## Approach

```python
from sqlalchemy import event


class count_queries:
    def __init__(self, engine):
        self.engine = engine
        self.statements = []

    def _record(self, conn, cursor, statement, parameters, context, executemany):
        self.statements.append(statement)

    @property
    def count(self):
        return len(self.statements)

    def __enter__(self):
        event.listen(self.engine, "before_cursor_execute", self._record)
        return self

    def __exit__(self, exc_type, exc, tb):
        event.remove(self.engine, "before_cursor_execute", self._record)
        return False
```

The listener is a bound method (`self._record`), which is a **different object each time you write it**, but `event.remove` compares them by equality, so it finds the one registered. Each counter has its own list, so nesting works: both listeners are active during the inner block, and only the outer one stays after it. Returning `False` from `__exit__` lets exceptions continue, as they should.

Example: a block with one `select(Customer)` leaves `q.statements == ["SELECT customers.id, customers.name FROM customers"]` and `q.count == 1`.

## Complexity

`O(1)` per statement.

## Another way

A `contextlib.contextmanager` generator with `try/finally` is shorter but cannot expose `count` as a property without a small object. The class form is clearer here.

## Why it matters

This tiny tool turns "the page feels slow" into a number, and (problem 54) into a test that fails when someone reintroduces an N+1.
