## Approach

Index 0 is the first character. Index -1 is the last one, because Python adds the length to a negative index. `len()` counts the characters.

## Code

```python
text = input()
print(f"First: {text[0]}")
print(f"Last: {text[-1]}")
print(f"Length: {len(text)}")
```

## Why it works for one character

For `"a"`, both `text[0]` and `text[-1]` refer to the same position, so first and last are both `a`. Nothing special is needed.

## Another way

`text[len(text) - 1]` also gives the last character. It works, but `text[-1]` is shorter and cannot be off by one.
