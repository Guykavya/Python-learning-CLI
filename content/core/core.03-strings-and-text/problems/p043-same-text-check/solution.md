## Code

```python
import unicodedata

a = input()
b = input()
na = unicodedata.normalize("NFC", a).casefold()
nb = unicodedata.normalize("NFC", b).casefold()
print(f"Exact: {a == b}")
print(f"Ignoring case: {a.casefold() == b.casefold()}")
print(f"Normalised: {na == nb}")
print(f"Lengths: {len(a)} {len(b)}")
```

## Why casefold alone is not enough

`"CAFÉ".casefold()` is `"café"`: still five code points, still not equal to the four code points of `"café"`. Casefolding changes letters, not the way they are composed.

## Why normalise

NFC combines a base letter and a combining mark into one code point wherever such a code point exists. After that, the two forms are the same sequence.

## Another way

`NFD` (decompose everything) works just as well for comparing, as long as both sides use the same form. Python's own documentation suggests `NFD(NFD(s).casefold())` for the most careful comparison; for most text NFC then casefold is enough.
