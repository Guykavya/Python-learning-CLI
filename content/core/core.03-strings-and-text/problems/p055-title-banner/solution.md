## Code

```python
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

## Why `textwrap.shorten`

It does three jobs at once, with no `if` needed: it collapses whitespace, leaves text that fits alone, and otherwise drops whole words and adds the placeholder. If even the first word does not fit, the result is just the placeholder.

## Why not `str.center`

`"ab".center(5)` gives `"  ab "`: CPython's `center` can put the odd extra space on the **left**. The f-string `^` always puts it on the right. Small differences like this are exactly what tests catch.

## Another way

`f"{text:^{inner}}"` could also be written `format(text, f"^{inner}")`.
