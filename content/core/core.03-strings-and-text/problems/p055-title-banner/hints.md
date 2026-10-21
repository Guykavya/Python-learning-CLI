## Hint 1

The width of the middle area depends on `W`. How can a format spec use a width stored in a variable?

## Hint 2

`inner = W - 4`. Then `text = textwrap.shorten(title, width=inner, placeholder="...")` and `f"| {text:^{inner}} |"`.

## Hint 3

```
import textwrap
title = input()
w = int(input())
inner = w - 4
text = textwrap.shorten(title, width=inner, placeholder="...")
edge = "+" + "-" * (w - 2) + "+"
print(edge)
print(f"| {text:^{inner}} |")
print(edge)
```
