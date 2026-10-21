## Code

```python
import textwrap

width = int(input())
text = input()
print(textwrap.fill(text, width))
print("-" * width)
print(textwrap.shorten(text, width, placeholder=" ..."))
```

## What each call does

- `fill` breaks at spaces so every line is at most `width` long, and joins the lines with `\n`.
- `shorten` first collapses all whitespace, then, only if the result is too long, drops whole words from the end until the words plus the placeholder fit.

## Another way

`"\n".join(textwrap.wrap(text, width))` is exactly what `fill` does.
