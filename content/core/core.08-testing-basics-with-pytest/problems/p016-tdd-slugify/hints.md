## Hint 1

Start with the first failing test only. What is the least code that returns `"hello"` for `"Hello"`? It is fine if it fails the later tests.

## Hint 2

`text.split()` with no argument splits on any run of whitespace and ignores the ends. What does that give you for rules 2, 3 and 6?

## Hint 3

```
words = []
for word in text.lower().split():
    kept = ""
    for ch in word:
        if ch.isalnum():
            kept += ch
    if kept != "":
        words.append(kept)
return "-".join(words)
```
