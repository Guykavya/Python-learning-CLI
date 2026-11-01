## Hint 1

What goes wrong in the draft when a handler removes itself while the `for` loop is walking the
same list? What do you loop over instead? And what must wrap the call `fn(**data)` so that one
bad handler cannot end the loop? Which exceptions should you catch?

## Hint 2

If the same function can be subscribed twice, `list.remove(fn)` removes the wrong one. Give each
subscription its own identity, for example a one-item tuple `(fn,)` created in `subscribe`, and
remove the entry with `is`.

```
subscribe(event, fn):
    entry = (fn,)
    store entry in the event's list
    def unsubscribe(): find entry by identity; delete it if present (safe to repeat)
    return unsubscribe

publish(event, **data):
    errors = []
    for each entry in a COPY of the list:
        try: fn(**data)
        except Exception as exc: errors.append(exc)
    return errors
```
