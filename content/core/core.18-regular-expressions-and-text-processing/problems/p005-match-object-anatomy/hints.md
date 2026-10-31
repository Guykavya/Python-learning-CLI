## Hint 1

Call `m = re.search(pattern, text)`. What are `m.group(0)`, `m.start()` and `m.end()` for `re.search(r"\d+", "order 66 shipped")`? Check that `text[m.start():m.end()]` gives the same text as `m.group(0)`.

## Hint 2

How do you tell "no match" apart from "matched the empty string"? `m` is `None` in the first case. In the second, `m` is a Match object whose `group(0)` is `""`, which is falsy. So test `m`, not the group.

## Hint 3

```
span_info(pattern, text):
    m = re.search(pattern, text)
    if m is None: return None
    return (m.group(0), m.start(), m.end())
```
