## Code

```python
import string

table = str.maketrans("", "", string.punctuation + string.whitespace)
cleaned = input().translate(table).casefold()
print(f"Cleaned: {cleaned}")
print(f"Palindrome: {cleaned == cleaned[::-1]}")
```

## Order of steps

Delete first, casefold second, or the other way round: both work here, because casefolding never creates punctuation. But casefold **before** comparing, or `W` and `w` will not match.

## Another way

`"".join(cleaned.split())` removes whitespace without `string.whitespace`, and a second translate table removes punctuation. One combined table is simpler and does a single pass.

## Limits

Accented letters are kept as they are, so `"Ésé"` works, but `"é"` and `"e"` are not treated as the same letter. Curly quotes and other non-ASCII punctuation are not removed.
