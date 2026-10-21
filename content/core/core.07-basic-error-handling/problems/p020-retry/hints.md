## Hint 1

`except errors as e:` works when `errors` is a tuple of classes, just like a written-out tuple.

## Hint 2

After the loop ends, you are outside the handler, so `e` no longer exists. What can you do
inside the handler so the exception is still available afterwards?

## Hint 3

```
if attempts < 1: raise ValueError(...)
last_error = None
for _ in range(attempts):
    try: return func()
    except errors as e: last_error = e
raise last_error
```
