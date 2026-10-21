**1.** In `show`, `visits` is never assigned, so it is not a local name. Python looks it up by
LEGB: no local, no enclosing function, so it finds the **global** `visits`.

**2.** Python decides which names are local **when it compiles the function**, before any line
runs. The rule: a name assigned anywhere in a function body is local for the **entire** body.
`record` contains `visits = ...`, so `visits` is local everywhere in `record`, including the
`print` line above the assignment. When the `print` runs, the local `visits` has no value yet,
and Python never falls back to the global, so it raises `UnboundLocalError`.

**3.** `record.__code__.co_varnames` is `('visits',)`, showing that the compiler made
`visits` a local variable. For `show`, `co_varnames` is `()`.

**4.** Fix A, preferred: make the function pure. Pass the count in and return the new one:

```python
def record(visits):
    print("visits:", visits)
    return visits + 1

visits = record(visits)
```

Everything the function uses is visible in the call, it is easy to test, and nothing far away
changes behind your back. Fix B: add `global visits` as the first line of `record`. It works,
but it hides a dependency on module state and makes testing and reasoning harder. (If the
function did not need to change the global at all, a third fix is a different local name,
`new_visits = visits + 1`.)

**5.** No. `visits_list.append(1)` does not assign the name `visits_list`; it calls a method on
the object the name refers to. So the name is not local, LEGB finds the global list, and the
list is mutated. `global` is only needed to **rebind** a global name.

Key ideas to check: locality decided at compile time for the whole body; no fallback to global;
`co_varnames`; prefer parameters and return values; mutation does not need `global`.
