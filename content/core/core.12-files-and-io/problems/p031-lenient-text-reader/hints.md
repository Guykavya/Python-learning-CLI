## Hint 1

Which exception does Python raise when a byte is not valid in the chosen encoding? How can you try one thing and
then do another if it fails? Which argument of `open` decides what happens with bad bytes?

## Hint 2

```
try:
    with open(path, encoding="utf-8") as f:
        return f.read(), False
except UnicodeDecodeError:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read(), True
```
