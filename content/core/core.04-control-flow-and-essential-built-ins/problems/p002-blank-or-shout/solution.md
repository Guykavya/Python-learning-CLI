## Approach

Strip the line once. An empty string is falsy, so `if not text:` detects a blank line.
Otherwise build the shout.

## Code

```python
text = input().strip()
if not text:
    print("(blank)")
else:
    shout = text.upper()
    print(shout if shout.endswith("!") else shout + "!")
```

## Why `"0"` is not blank

`"0"` is a string with one character. Only the empty string is falsy, so `"0"` is shouted
as `0!`. Python never looks at what a string *means*.

## Another way

`if text == "":` or `if len(text) == 0:` are the same test. `if not text:` is the usual Python style.
