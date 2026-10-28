**1. What happens.** The two managers differ only in the `try`/`finally` around `yield`. In `opened("a")` the block raises `RuntimeError`. With `@contextmanager`, the exception is **thrown into the generator at the `yield` line**: `yield` itself raises the exception there. The code after `yield` (`log.append("close a")`) is only reached if `yield` returns normally, so it is **skipped**, and the generator ends with the exception. The output shows `open a`, `work a`, `caught boom` and no `close a`: the clean-up never ran. In `safe_opened("b")` the same exception arrives at `yield`, which is inside a `try`; the `finally` runs (`close b`), then the exception continues to the outer `except` (`caught boom`).

**2. Why it works this way.** A class-based manager has a method `__exit__` that Python **always** calls. A generator has no such method; `@contextmanager` builds one that resumes the generator after `yield`. If the block failed, it resumes by raising the exception at the `yield`. So the generator must handle the failure the way any normal function would: with `try`/`finally`. Nothing "magic" runs the clean-up for you.

**3. The fix.**

```python
@contextmanager
def opened(name):
    log.append("open " + name)
    try:
        yield name
    finally:
        log.append("close " + name)
```

Use `finally` when the clean-up must always run (close a file, release a lock, restore a setting). Use `except SomeError:` around `yield` if the manager should react to (or swallow) a specific error; if you catch it and do not re-raise, the exception is swallowed, just like `__exit__` returning `True`.

**4. When it matters.** Whenever the clean-up frees something that must not leak: an open file or socket, a lock (not releasing it blocks every other thread forever), a changed global such as the current directory or an environment variable (not restoring it leaves the program in a wrong state for the rest of the run), a database transaction. Without a `try`/`finally` the manager still *looks* right in tests where nothing fails.
