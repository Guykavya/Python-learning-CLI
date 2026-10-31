## Approach

`(\w+)` captures a word, `\s+` eats the gap, and `\1` demands the very same text again.
Three details make it correct:

- `\b` at the **start** stops the word being the tail of a longer word. Without it,
  `this is` matches: `(\w+)` takes `is` from inside `this`.
- `\b` at the **end** stops `\1` from being the start of a longer word: `the theory`.
- `re.IGNORECASE` applies to the backreference too, so `\1` = `the` also matches `The`.

`finditer` gives every match; `m.group(1)` is the first copy, spelled as written.

## Code

```python
import re

DOUBLED_RE = re.compile(r"\b(\w+)\s+\1\b", re.IGNORECASE)


def doubled_words(text: str) -> list[str]:
    return [m.group(1) for m in DOUBLED_RE.finditer(text)]
```

## Complexity

For each start position the engine tries word lengths and compares; in practice this is close
to O(n) because words are short. O(k) extra memory for k results.

## Another way

`re.findall(pattern, text, re.IGNORECASE)` returns group 1 directly, because the pattern has
exactly one group. Without regex: split into words with their gaps and compare each word with
the next one using `.lower()` (or `.casefold()`), which is longer and loses the positions.
