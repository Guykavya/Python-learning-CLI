# A test helper that guards against N+1

Chapter section 18.5. The best protection against an N+1 coming back is a **test that fails** when a function runs too many queries. Write the context manager

```python
with assert_max_queries(engine, n):
    ...code under test...
```

- While the block runs it records the SQL statements the engine executes.
- When the block ends **normally**, if more than `n` statements ran it raises **`AssertionError`** whose message says the limit, the real count and the **list of the statements**, numbered (so that the repeated statement is easy to see), for example:

  ```text
  expected at most 2 queries, but 4 ran:
    1. SELECT ... FROM orders
    2. SELECT ... FROM customers WHERE ? = customers.id
    3. SELECT ... FROM customers WHERE ? = customers.id
    4. SELECT ... FROM customers WHERE ? = customers.id
  ```
- With `n` queries or fewer, it does nothing. `n = 0` is allowed (no query at all).
- If the **block itself raises** an exception, that exception passes through unchanged (do not hide it behind your assertion).
- The listener is always removed at the end.

## Example

```python
with assert_max_queries(engine, 2):
    orders_page(session)            # fine with selectinload; an AssertionError listing 101 statements with the N+1 version
```
