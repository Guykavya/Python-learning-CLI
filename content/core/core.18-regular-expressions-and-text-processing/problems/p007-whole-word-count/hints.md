## Hint 1

What does `re.findall(r"\bcat\b", "cats cat scat")` return? Why does `cats` not match? Then try `re.findall(r"\bcat\b", "CAT", re.IGNORECASE)`.

## Hint 2

`word` comes from the caller, so you cannot write it into the pattern by hand. You build the pattern from a string. What happens to the `.` in `"node.js"` if you just glue it between two `\b`s? Which function makes it literal?

## Hint 3

```
count_word(text, word):
    pattern = r"\b" + re.escape(word) + r"\b"
    return len(re.findall(pattern, text, re.IGNORECASE))
```
