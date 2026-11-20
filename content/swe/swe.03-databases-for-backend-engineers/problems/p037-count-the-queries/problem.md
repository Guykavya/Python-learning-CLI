# Count the queries

Chapter sections 10.3 and 18.5. You cannot fix an N+1 problem you cannot see. Write a context manager

```python
with count_queries(engine) as q:
    ...                       # code that uses the database
q.count                       # how many SQL statements the engine received
q.statements                  # their texts, in order
```

- While the `with` block runs, record the SQL text of every statement the engine executes (SQLAlchemy event `before_cursor_execute`). `q.count` is the number of statements, `q.statements` the list of texts.
- When the block ends (normally **or with an exception**) the listener is **removed**: statements run afterwards are not counted, and nothing stays registered on the engine.
- Two counters can be **nested** or sequential; each counts only what happened while it was active (the outer one also sees the statements of the inner block).
- `count_queries(engine)` is a context manager that returns itself from `__enter__` (a class with `__enter__`/`__exit__`, or `contextlib.contextmanager`); it must not suppress exceptions.

## Example

```python
with count_queries(engine) as q:
    session.execute(select(Customer))
    session.execute(select(Order))
q.count       # 2
```
