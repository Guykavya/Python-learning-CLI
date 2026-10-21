## Hint 1

Remove the optional `#` first. Which method removes something only if it is there?

## Hint 2

`code = text.strip().removeprefix("#")`. Then the pairs are `code[0:2]`, `code[2:4]`, `code[4:6]`. Convert each with `int(pair, 16)`.

## Hint 3

```
code = input().strip().removeprefix("#")
r = int(code[0:2], 16)
g = int(code[2:4], 16)
b = int(code[4:6], 16)
print(f"rgb({r}, {g}, {b})")
print(f"#{r:02x}{g:02x}{b:02x}")
```
