## Hint 1

When is a default value evaluated: once when `def` runs, or on every call?

## Hint 2

Default to `None`, and create the list inside the body, which runs on every call:
```
if guests is None:
    guests = []
guests.append(name)
return guests
```
Why `is None` and not `if not guests`? Think about a caller who passes their own **empty** list.
