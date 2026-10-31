## Approach

1. Escape each word with `re.escape` so characters like `.` are literal.
2. Join them with `|` and wrap the alternation in a **non-capturing group** with `\b` on both
   sides: `\b(?:darn|cat)\b`. Without the group, `|` would split the whole pattern into
   `\bdarn` OR `cat\b`.
3. Compile with `re.IGNORECASE`.
4. Call `subn` with a replacement **function**: it gets the `Match` and returns
   `"*" * len(m.group())`, so `"DARN"` becomes four stars.
5. Guard the empty list: the pattern `\b(?:)\b` matches the empty string at every word edge, and
   `subn` would insert stars there and report a non-zero count.

## Code

```python
import re


def censor(text: str, words: list[str]) -> tuple[str, int]:
    if not words:
        return (text, 0)
    alternatives = "|".join(re.escape(w) for w in words)
    pattern = re.compile(rf"\b(?:{alternatives})\b", re.IGNORECASE)
    return pattern.subn(lambda m: "*" * len(m.group()), text)
```

## Complexity

Building the pattern is O(total length of the words). One pass over the text: roughly
O(n · w) in the worst case for w words, because each position may try every alternative.

## Another way

Count separately: `new = pattern.sub(repl, text)` and `count = len(pattern.findall(text))`.
It works but scans the text twice; `subn` does both in one pass.
