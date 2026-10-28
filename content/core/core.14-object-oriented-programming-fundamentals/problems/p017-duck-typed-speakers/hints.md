## Hint 1

`thing.speak` (no brackets) only **looks up** the method; `thing.speak()` looks it up and calls it.
If both happen inside one `try`, can you tell which of the two raised the `AttributeError`?

## Hint 2

Keep the `try` as small as possible: only the lookup goes inside. The call goes after the `try`
block, so its errors are not caught.

```
results = []
for thing in things:
    try:
        speak = thing.speak          # lookup only
    except AttributeError:
        continue                     # no speak: skip it
    results.append(speak())          # call outside the try
return results
```
