## Approach

One pattern for one term, applied with `finditer`:

```
(?: (?P<key>\w+) : )?  (?: "(?P<quoted>[^"]*)" | (?P<word>\S+) )
```

- The key part is optional. The engine first tries **with** a key; if no value can follow the
  colon (a space or the end), it backtracks and tries **without** the key, so `\S+` takes the
  whole `tag:` as a free word. Backtracking does the "dangling key" rule for us.
- Alternatives are tried left to right, so the quoted form must come first; otherwise `\S+` would
  grab `"Jane` and stop at the space.
- If the closing quote is missing, the quoted alternative fails and `\S+` takes the term with the
  quote as an ordinary character.
- `finditer` skips the whitespace between terms because no term can start with whitespace.

For each match, the group that took part is the one that is not `None`. Test with `is not None`:
an empty quoted value `""` is falsy but present. `setdefault(key, [])` creates the list the first
time, and a plain dict keeps first-seen key order.

## Code

```python
import re

TERM = re.compile(
    r"""
    (?: (?P<key>\w+) : )?
    (?:
        "(?P<quoted>[^"]*)"
      | (?P<word>\S+)
    )
    """,
    re.VERBOSE,
)


def parse_query(q: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for m in TERM.finditer(q):
        key = m.group("key")
        key = key.lower() if key is not None else "_"
        value = m.group("quoted") if m.group("quoted") is not None else m.group("word")
        result.setdefault(key, []).append(value)
    return result
```

## Complexity

O(n) for a query of length n: each character is consumed by one term.

## Another way

Use `collections.defaultdict(list)` for the result and `return dict(result)` at the end. Or split
the job in two: first find terms with `"[^"]*"|\S+`, then check each term with
`re.fullmatch(r'(\w+):(.+)', term)`. Two small patterns can be easier to read than one, but the
quoted value after a key (`author:"Jane Doe"`) then needs the first pattern to allow `\w+:"..."`.
