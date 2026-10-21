## Code

```python
word = input()
width = int(input())
print(f"[{word:<{width}}]")
print(f"[{word:>{width}}]")
print(f"[{word:^{width}}]")
print(f"[{word:*^{width}}]")
```

## How nested fields work

Python first fills in the inner `{width}` to build the spec, for example `<9`, and then formats `word` with that spec. Any part of a spec can be filled in this way.

## Odd padding

With `cat` in width 8 there are 5 spaces of padding. The f-string `^` puts 2 on the left and 3 on the right. `str.center()` follows a different rule and can put the extra space on the left, so it may not match.
