## Hint 1

`run_all` is a normal loop with a `try/except Exception` **inside** it, so one failure does not end
the loop. Collect the caught exceptions in a list. After the loop, if the list is not empty, raise
one `ExceptionGroup` holding all of them. What is the first argument of `ExceptionGroup`?

## Hint 2

In `summarise`, each `except*` clause takes **its** part of the group out, and the rest goes on to
the next clause. Several clauses can run for the same group. Inside a clause, `eg.exceptions` is a
tuple of just the matching ones. The success count is "all tasks minus all failures".

## Hint 3

```
run_all(tasks):
    results = {}; errors = []
    for name, func in tasks:
        try: results[name] = func()
        except Exception as err:
            err.add_note(f"task: {name}"); errors.append(err)
    if errors: raise ExceptionGroup(f"{len(errors)} of {len(tasks)} tasks failed", errors)
    return results

summarise(tasks):
    counts = all zero
    try: run_all(tasks)
    except* ValueError as eg: counts["value_errors"] = len(eg.exceptions)
    except* KeyError as eg:   ...
    except* Exception as eg:  ...
    counts["ok"] = len(tasks) - (sum of the three)
    return counts
```
