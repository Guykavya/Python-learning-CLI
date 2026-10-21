## Approach

`partition(" ")` cuts at the first space only and always returns three strings, so unpacking it into three names never fails.

## Code

```python
text = input().strip()
command, space, rest = text.partition(" ")
print(f"Command: {command}")
print(f"Rest: {rest}")
```

## Why not `split()`?

`text.split()` cuts at every run of whitespace, so the inner spaces in `hello to   everyone` would be lost. `text.split(" ", 1)` cuts once, but if there is no space it gives one piece, and `[1]` would crash. `partition` handles both cases.
