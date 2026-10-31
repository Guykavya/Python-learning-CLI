## Approach

The key fact: `@contextmanager` builds a class with `__enter__` and `__exit__` around your generator.
`__enter__` runs the generator up to the `yield`. `__exit__` is called with the exception details. If
there is no exception it calls `next(gen)` and the code after `yield` runs. If there is one, it calls
`gen.throw(exc)`: the generator wakes up **at the `yield`** and the exception is raised there. A
`yield` that is not inside a `try`/`finally` lets the exception leave the generator at once, so the
lines below it never run.

## Code

```python
@contextmanager
def opened(name):
    log.append("open " + name)
    try:
        yield name
    finally:
        log.append("close " + name)
```

## Complexity

Not applicable: this is about control flow.

## Another way

Write the manager as a class with `__enter__` and `__exit__`. `__exit__` is always called, so the
clean-up code in it runs on both success and failure. That is the same guarantee, and is the reason
why class-based managers do not need a `try`/`finally`.
