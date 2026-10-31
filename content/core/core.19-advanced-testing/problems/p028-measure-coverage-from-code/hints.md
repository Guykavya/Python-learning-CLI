## Hint 1

Which steps must happen, in which order? Think of a stopwatch: you must press start before the thing you want to time happens. What has to be
on disk for coverage to measure it, and which of your steps creates it?

## Hint 2

`analysis2(path)` returns five things; two of them matter: the list of **statements** (line numbers of real code) and the list of **missing**
lines. Percent is `(len(statements) - len(missing)) / len(statements)`. Wrap each call in its own `try` / `except Exception`.

```
with TemporaryDirectory() as tmp:
    path = (Path(tmp) / "target_mod.py").resolve(); write source
    cov = coverage.Coverage(data_file=None, include=[str(path)])
    cov.start()
    try:   import module from path;  for args in calls: try func(*args) except Exception: pass
    finally: cov.stop()
    _, statements, _, missing, _ = cov.analysis2(str(path))
return round(100 * done / len(statements), 1), sorted(missing)
```
