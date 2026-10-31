## Hint 1

Write a pattern for one header line. Which characters are special in a regex and need escaping
(`+`)? How do you write "a comma and a number, but maybe not there at all" so that the number is
a group that can be `None`? And what flag makes `^` match at the start of **every** line?

## Hint 2

```
HUNK = ^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@      with re.MULTILINE
for m in HUNK.finditer(text):
    a, b, c, d = m.groups()
    append (int(a), int(b) if b is not None else 1, int(c), int(d) if d is not None else 1)
```
