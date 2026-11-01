- Putting `try/except` around `t.start()` or `t.join()` in the main thread. The exception lives
  in the other thread's stack; it never reaches these calls.
- Storing `str(exc)` or `type(exc)`. You lose the traceback and the exception type (or the
  message). Keep the object; the caller can re-raise it with `raise exc`.
- Using a bare `except:` or `except BaseException:`. That also swallows `KeyboardInterrupt` and
  `SystemExit`, which should not be treated as normal job failures.
- Appending to a shared list from each thread. The order becomes finish order, and readers
  cannot tell which entry belongs to which function.
- Assuming `join()` tells you whether the thread succeeded. It returns `None` either way.
