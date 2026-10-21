See the model answer shown when you check. The ideas that must appear:

1. Choice 1: `NameError` from the typo `balanse`, hidden and blamed on the user.
2. Choice 3: `sys.exit()` raises `SystemExit`, caught by the bare except.
3. Ctrl+C raises `KeyboardInterrupt`, also caught when it happens inside the `try`.
4. `except Exception` lets `SystemExit` and `KeyboardInterrupt` through (they are not
   `Exception` subclasses) but still hides `NameError`.
5. Catch only `ValueError` around the amount conversion; fix the typo; let bugs crash.
