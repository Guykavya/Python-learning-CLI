## Approach

```python
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
```

The check happens in `__exit__`, after the code under test ran, so the **whole** list of statements is available for the message. The `exc_type is None` test keeps a real error of the block visible: an assertion about query counts must not replace the traceback of a crash. The numbered list makes the N+1 signature visible: **the same statement repeated**, differing only in the parameter.

Example: with `n=2` and four statements, the message ends with the three `customers` statements, which is exactly the loop that lazy-loaded `order.customer`.

## Complexity

`O(statements)`.

## Another way

`pytest` fixtures can wrap this (`def test_page(max_queries): with max_queries(2): ...`), and some projects add such a check to every request in their test client. `django-assert-num-queries` is the same idea for Django.

## Why it matters

A performance test that fails when someone reintroduces an N+1 is worth more than a code review remark. The first time you see its message pointing at the exact repeated statement, you will keep it.
