- Printing `open` right after `w = worker()`. Calling a generator function runs nothing.
- Forgetting the `None` line. `throw` returns the next yielded value, like `send` and `next`.
- Thinking `throw` kills the generator. It only does if the generator does not catch the error.
  Here the inner `except` catches it and the loop goes on.
- Writing `bad job:` for `close()`. `close()` raises `GeneratorExit`, which is not a `ValueError`.
- Expecting `close()` to raise an error in the main program. It swallows `GeneratorExit`.
- Expecting `cleanup` for `w2`. The `finally` only runs if the body entered the `try`.
