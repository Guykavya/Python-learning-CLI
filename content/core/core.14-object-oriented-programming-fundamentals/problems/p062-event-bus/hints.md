## Hint 1

What data structure maps an event name to the listeners of that name, in order? How do you check
"has a callable `handle`" without crashing when there is no `handle` at all? (`getattr` has a
default argument.)

Why compare listeners with `is` and not `==` or `in`? (`in` uses `==`, and a class may define `==`
in strange ways; here we mean "the same object".)

## Hint 2

In `publish`, build the list of targets **first**, as a new list (specific listeners + `"*"`
listeners). Then loop over that copy. Why does this one decision solve both "subscribe during publish"
and "unsubscribe during publish"?

Catch `Exception`, not `BaseException`: a `KeyboardInterrupt` should still stop the program.

## Hint 3

```text
publish(name, payload):
    if name == "*": raise ValueError(...)
    event = Event(name, payload)
    targets = copy of listeners[name] + copy of listeners["*"]
    errors = []
    for listener in targets:
        try: listener.handle(event)
        except Exception as exc:
            exc.add_note(f"listener: {type(listener).__name__}")
            errors.append(exc)
    if errors: raise ExceptionGroup(f"{len(errors)} listener(s) failed for {name!r}", errors)
    return len(targets)
```
