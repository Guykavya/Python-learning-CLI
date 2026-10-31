# Measure coverage from code

`coverage` is a program (`python -m coverage run ...`) but also a library. In this problem you use the library to answer
"which lines did these calls run?" without leaving any files behind.

Write `measure(source, func_name, calls)`:

- `source` is the text of a small Python module, `func_name` the name of a function defined in it, and `calls` a list of argument tuples.
- Run `func_name(*args)` for every `args` in `calls`. If a call raises an exception, ignore it and carry on.
- Return `(percent, missing)`: the **line coverage** of the whole `source` as a float rounded to one decimal, and the sorted list of line numbers
  (1-based, counted in `source`) that never ran. Blank lines and comments are not statements, so they never count.

```python
GRADE = """def grade(n):
    if n >= 90:
        return "A"
    if n >= 50:
        return "B"
    return "F"
"""
measure(GRADE, "grade", [(95,), (10,)])    # (83.3, [5])   line 5, return "B", never ran
measure(GRADE, "grade", [(95,), (60,), (10,)])   # (100.0, [])
```

The API you need (chapter section 11):

```python
cov = coverage.Coverage(data_file=None, include=[path])   # data_file=None: keep the data in memory, write no .coverage file
cov.start()   ...   cov.stop()
filename, statements, excluded, missing, missing_text = cov.analysis2(path)
```

Rules of the game:

- coverage measures **files**, so write `source` into a file inside a `tempfile.TemporaryDirectory()` and load it with
  `importlib.util.spec_from_file_location` (then `module_from_spec` and `spec.loader.exec_module`). Do not use `exec`.
- Start measuring **before** you import the module, so the `def` line counts as run.
- Always call `cov.stop()`, even if something fails (`try` / `finally`).
- Leave no files behind: the checker looks at the current folder.

The checker also works when it is itself running under `pytest`.
