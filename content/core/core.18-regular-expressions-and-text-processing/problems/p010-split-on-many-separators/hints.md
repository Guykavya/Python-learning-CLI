## Hint 1

Write one character class that matches a single separator: comma, semicolon or any whitespace. What does `re.split(r"[,;\s]", "a,,b")` return? Where do the empty strings come from?

## Hint 2

Add a quantifier so a run of separators is one split. Even then, `re.split(r"[,;\s]+", " a ")` returns `['', 'a', '']`: a separator at the very start or end still leaves an empty piece. How can you keep only the non-empty pieces?

## Hint 3

```
tokens(s):
    parts = re.split(r"[,;\s]+", s)
    return [p for p in parts if p != ""]
```
