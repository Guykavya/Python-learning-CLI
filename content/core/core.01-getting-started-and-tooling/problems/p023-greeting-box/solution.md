## Approach

Every line's length depends on one number: the message length plus the two
padding spaces. Compute it once and build every line from it.

## Code

```python
name = input()
message = "Hello, " + name + "!"
width = len(message) + 2

border = "+" + "-" * width + "+"
empty = "|" + " " * width + "|"
print(border)
print(empty)
print("| " + message + " |")
print(empty)
print(border)
```

## Why `+ 2`

The middle line is `| ` + message + ` |`. Between the two `|` characters there
are the message and one space on each side: `len(message) + 2` characters. The
border and empty lines must fill exactly that same space.

## Another way

You could compute `len(name) + 9` directly (7 for `"Hello, "`, 1 for `!`, 2 for
padding). It works, but a "magic number" like 9 hides the reasoning. Naming
`message` and `width` makes the code explain itself (Readability counts).
