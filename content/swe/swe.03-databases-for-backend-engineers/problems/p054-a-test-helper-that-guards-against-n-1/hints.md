## Hint 1

You wrote almost the same thing in problem 37. What is different? Where in the context manager can you decide that the test failed?

## Hint 2

In `__exit__`: it receives the exception of the block (or `None`). Only when the block ended **without** an exception should you compare the count with `n` and raise `AssertionError`.

## Hint 3

```text
__enter__: listen; return self
__exit__(exc_type, exc, tb): remove the listener; if exc_type is None and len(statements) > n: raise AssertionError(message with numbered statements); return False
```
