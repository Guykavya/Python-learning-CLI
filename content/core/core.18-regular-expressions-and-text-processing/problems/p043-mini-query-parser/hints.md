## Hint 1

Describe **one term** as a pattern and let `finditer` find all of them; whitespace between terms
is skipped automatically. A term is: an optional `key:` part, then a value. The value is either
a quoted phrase or a run of non-spaces. Which of the two must be tried first, and why?

## Hint 2

Make the key part an optional group `(?:(?P<key>\w+):)?`. When it is followed by a space, the
value part cannot match there, so the engine backtracks: it drops the optional key and lets
`\S+` take `tag:` as a free word. That is exactly the rule in the statement.

```
TERM = (?: (?P<key>\w+) : )?  (?: "(?P<quoted>[^"]*)" | (?P<word>\S+) )
result = {}
for m in TERM.finditer(q):
    key = lower(m["key"]) if it is not None else "_"
    value = m["quoted"] if it is not None else m["word"]
    result.setdefault(key, []).append(value)
```
