## Code

```python
import string

text = input()
print(f"title: {text.title()}")
print(f"capwords: {string.capwords(text)}")
print(f"capitalize: {text.capitalize()}")
```

## The differences

| Tool | Word boundary | Spaces | Result for `they're` |
|---|---|---|---|
| `title()` | any non-letter | kept | `They'Re` |
| `capwords()` | whitespace only | collapsed to one | `They're` |
| `capitalize()` | only the first character | kept | `They're` (rest lowercased) |

`capwords(s)` is just `" ".join(w.capitalize() for w in s.split())`. That is why it collapses spaces.

## Which to use

For headings typed by people, `capwords` usually looks best. None of them is perfect: real title rules keep small words like "of" lowercase, which needs more logic.
