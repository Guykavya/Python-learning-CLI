## Code

```python
import string

table = str.maketrans("", "", string.punctuation)
words = input().translate(table).casefold().split()
print(f"Words: {len(words)}")
print(" ".join(words))
```

## Why `translate`

There are 32 punctuation characters. Removing them with `replace` would need 32 calls, each walking the whole text. `translate` walks the text once.

## Why remove punctuation before splitting

If you split first, `world!` and `world` are different words. Cleaning first makes them the same.

## A limit worth knowing

`string.punctuation` is ASCII only. Curly quotes (`“ ”`), the long dash (`—`) and `¿` are not in it and will survive. Real text tools handle this with `unicodedata.category` or regular expressions (core.04).
