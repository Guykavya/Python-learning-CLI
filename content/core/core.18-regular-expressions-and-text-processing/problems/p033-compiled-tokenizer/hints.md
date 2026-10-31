## Hint 1

Write the five token kinds as a list of `(name, regex)` pairs. How can you turn that list into
**one** pattern where each piece is a named group? After a match, which `Match` attribute names
the group that matched?

## Hint 2

The order matters: `|` tries alternatives left to right, and `MISMATCH` (`.`) must be last, or
it would win every time. `finditer` walks the whole text because `MISMATCH` and `SKIP` together
can match any character.

```
__init__:
    spec = [("NUMBER", r"\d+(?:\.\d+)?"), ("NAME", ...), ("OP", ...), ("SKIP", r"\s+"), ("MISMATCH", r".")]
    self.pattern = compile("|".join("(?P<" + name + ">" + rx + ")" for each pair))

tokens(text):
    for m in self.pattern.finditer(text):
        kind = m.lastgroup
        if kind == "SKIP": continue
        if kind == "MISMATCH": raise ValueError(... m.group() ... m.start())
        yield (kind, m.group())
```
