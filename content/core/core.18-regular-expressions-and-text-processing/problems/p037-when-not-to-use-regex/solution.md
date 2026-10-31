## Approach

Judge each tool by the **shape of the data**:

- Formats with a grammar and a standard parser (HTML, JSON, CSV, TOML) → use the parser. A regex
  sees only characters, not the structure, so quoting, nesting, escaping and alternative spellings
  break it.
- Nested structure (brackets, tags) → a counter or a stack. Regular expressions have finite memory
  and cannot count without limit.
- Fixed text (one separator, one suffix) → string methods: simpler, faster, nothing to escape.
- Flat patterns (an id format, a date, a log line) → regex shines.

The full model answer is in `answer.md`.

## Complexity

The balanced-bracket counter is O(n) time and O(1) memory (a stack is O(depth) memory). Parsers
like `json.loads` are O(n) too, so correctness costs nothing.

## Another way

For part c in code:

```python
def balanced(s):
    depth = 0
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0
```
