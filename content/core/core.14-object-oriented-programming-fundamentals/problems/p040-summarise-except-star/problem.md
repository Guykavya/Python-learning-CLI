# Run every task, then sort the failures

A nightly job runs many small tasks (import a file, send a mail, ...). One failing task must not
stop the others. At the end, the job reports **all** failures together. Python 3.11 has a tool made
for this: `ExceptionGroup`, and `except*` to handle the different kinds inside it. Write two
functions in `solution.py`.

**`run_all(tasks)`**

- `tasks` is a list of `(name, func)` pairs. Call every `func()` with no arguments, in order, even
  after some have failed.
- Catch only `Exception` (not `KeyboardInterrupt` and friends). Before keeping a failed task's
  exception, add a note to it with `err.add_note(f"task: {name}")`.
- If nothing failed, return a dict `{name: result}` in task order.
- If something failed, raise `ExceptionGroup(f"{failed} of {total} tasks failed", errors)` where
  `errors` is the list of the exceptions, in task order.

**`summarise(tasks)`** calls `run_all(tasks)` and returns a dict with four counts:

```python
{"ok": ..., "value_errors": ..., "key_errors": ..., "other_errors": ...}
```

Use `except* ValueError`, `except* KeyError` and `except* Exception`. Inside an `except*` block the
name (`as eg`) is an exception group of just the matching exceptions, so `len(eg.exceptions)` counts
them. Subclasses count with their parent: a `UnicodeDecodeError` is a `ValueError`. An
`IndexError` is **not** a `KeyError` (they are siblings), so it is an "other". `ok` is the number of
tasks that did not fail.

**Example**

```python
def good():  return 1
def bad_int():  return int("x")          # ValueError
def bad_key():  return {}["missing"]     # KeyError
def bad_index(): return [][0]            # IndexError

run_all([("a", good), ("b", good)])      # {'a': 1, 'b': 1}

run_all([("a", good), ("b", bad_int), ("c", bad_key)])
# ExceptionGroup: 2 of 3 tasks failed (2 sub-exceptions)
#   the ValueError has the note 'task: b', the KeyError has 'task: c'

summarise([("a", good), ("b", bad_int), ("c", bad_key), ("d", bad_index), ("e", bad_int)])
# {'ok': 1, 'value_errors': 2, 'key_errors': 1, 'other_errors': 1}
```
