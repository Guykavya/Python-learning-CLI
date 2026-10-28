## Approach

**Why a group?** A normal `raise` can carry only one exception. When several independent things
failed, choosing one and hiding the rest loses information. An `ExceptionGroup` carries all of them
(chapter section 19).

**`run_all`.** The `try` is *inside* the loop, so the loop continues after a failure. Each caught
exception gets a note (`add_note`, section 18), so the report later says which task it came from:
an exception object itself does not know the task's name. Catching `Exception`, not everything,
lets Ctrl+C (`KeyboardInterrupt`) still stop the job.

**`summarise` with `except*`.** `except*` works differently from `except`:

- Every `except*` clause looks at the group. It takes out the exceptions that match its type
  (subclasses included) and runs with `eg` = a smaller group of just those.
- What is left goes on to the next clause. So for one group, **several** clauses can run: here the
  `ValueError`, `KeyError` and `Exception` clauses all run for the mixed example.
- `except* Exception` at the end catches whatever is left, so nothing escapes.

`KeyError` and `IndexError` are both `LookupError`s, but neither is a subclass of the other. So an
`IndexError` is not caught by `except* KeyError`.

## Code

```python
def run_all(tasks):
    results = {}
    errors = []
    for name, func in tasks:
        try:
            results[name] = func()
        except Exception as err:
            err.add_note(f"task: {name}")
            errors.append(err)
    if errors:
        raise ExceptionGroup(f"{len(errors)} of {len(tasks)} tasks failed", errors)
    return results


def summarise(tasks):
    counts = {"ok": len(tasks), "value_errors": 0, "key_errors": 0, "other_errors": 0}
    try:
        run_all(tasks)
    except* ValueError as eg:
        counts["value_errors"] = len(eg.exceptions)
    except* KeyError as eg:
        counts["key_errors"] = len(eg.exceptions)
    except* Exception as eg:
        counts["other_errors"] = len(eg.exceptions)
    counts["ok"] -= counts["value_errors"] + counts["key_errors"] + counts["other_errors"]
    return counts
```

If `run_all` raises nothing, no `except*` clause runs and all failure counts stay 0.

## Complexity

O(n) for n tasks (plus the tasks' own work).

## Another way

Without `except*`, you can catch the whole group with `except ExceptionGroup as eg` and use
`eg.split(ValueError)`, which returns `(matching_group, rest_group)` (either may be `None`).
`except*` does that splitting for you. Note that `eg.exceptions` can contain nested groups; here
the group is flat, so its length is the number of failures. For nested groups you would walk the
tree (a deep problem later in this module does that).
