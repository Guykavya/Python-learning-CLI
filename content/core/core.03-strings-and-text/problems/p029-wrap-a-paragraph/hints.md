## Hint 1

Which module from section 23 reshapes paragraphs? You need to import it.

## Hint 2

`textwrap.fill(text, width)` returns one string with newlines in it. `textwrap.shorten(text, width, placeholder=" ...")` returns one line.

## Hint 3

```
import textwrap
width = int(input())
text = input()
print(textwrap.fill(text, width))
print("-" * width)
print(textwrap.shorten(text, width, placeholder=" ..."))
```
