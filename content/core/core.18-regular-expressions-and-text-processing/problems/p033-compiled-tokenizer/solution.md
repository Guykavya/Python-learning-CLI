## Approach

Each token kind is one named group; the master pattern is all of them joined with `|`:

```
(?P<NUMBER>\d+(?:\.\d+)?)|(?P<NAME>[A-Za-z_]\w*)|(?P<OP>[-+*/=()])|(?P<SKIP>\s+)|(?P<MISMATCH>.)
```

Exactly one group takes part in each match, and `m.lastgroup` is its name, so the kind comes for
free. `SKIP` covers whitespace and `MISMATCH` covers any other single character, so together the
alternatives can match at **every** position: `finditer` never silently jumps over text. That is
what lets us report bad characters.

The pattern is compiled once in `__init__`; each call to `tokens` only runs it. Because `tokens`
uses `yield`, tokens come out one at a time and an error appears only when the bad character is
reached.

## Code

```python
import re

TOKEN_SPEC = [
    ("NUMBER", r"\d+(?:\.\d+)?"),
    ("NAME", r"[A-Za-z_]\w*"),
    ("OP", r"[-+*/=()]"),
    ("SKIP", r"\s+"),
    ("MISMATCH", r"."),
]


class Tokenizer:
    def __init__(self):
        master = "|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_SPEC)
        self.pattern = re.compile(master)

    def tokens(self, text):
        for m in self.pattern.finditer(text):
            kind = m.lastgroup
            value = m.group()
            if kind == "SKIP":
                continue
            if kind == "MISMATCH":
                raise ValueError(f"unexpected character {value!r} at index {m.start()}")
            yield (kind, value)
```

## Complexity

O(n) for text of length n: one pass, each position tries at most five short alternatives.
Memory O(1) beyond the pattern, because it is a generator.

## Another way

Without `finditer`, walk with `pos` and `self.pattern.match(text, pos)`, moving `pos = m.end()`
each time. That style is useful when the next token kind depends on the previous one (for example
in a parser), because you can switch patterns between calls.
