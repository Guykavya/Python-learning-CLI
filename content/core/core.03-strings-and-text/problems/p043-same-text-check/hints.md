## Hint 1

Which module provides `normalize`? You need to import it.

## Hint 2

`import unicodedata`, then `unicodedata.normalize("NFC", text)` combines `E` + combining accent into the single code point `É`.

## Hint 3

```
import unicodedata
a = input()
b = input()
na = unicodedata.normalize("NFC", a).casefold()
nb = unicodedata.normalize("NFC", b).casefold()
print("Exact:", a == b)
print("Ignoring case:", a.casefold() == b.casefold())
print("Normalised:", na == nb)
print("Lengths:", len(a), len(b))
```
