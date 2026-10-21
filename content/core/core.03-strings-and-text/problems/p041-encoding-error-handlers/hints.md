## Hint 1

`text.encode("ascii", errors=...)` gives bytes. How do you turn ASCII bytes back into a `str` for printing?

## Hint 2

`text.encode("ascii", errors="replace").decode("ascii")`. For the last line: with `ignore`, every dropped character is missing from the result, so compare lengths.

## Hint 3

```
text = input()
kept = text.encode("ascii", errors="ignore").decode("ascii")
print("ignore:", kept)
print("replace:", text.encode("ascii", errors="replace").decode("ascii"))
... xmlcharrefreplace, backslashreplace ...
print("Lost:", len(text) - len(kept))
```
