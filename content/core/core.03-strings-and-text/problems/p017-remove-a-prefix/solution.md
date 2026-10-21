## Code

```python
tag = input()
print(f"Once: {tag.removeprefix('#')}")
print(f"All: {tag.lstrip('#')}")
```

## The difference

- `removeprefix(p)` removes the exact text `p` once, only if the string starts with it.
- `lstrip(chars)` treats its argument as a **set** of characters and removes them repeatedly from the left.

## Another way

Before Python 3.9 people wrote `tag[1:] if tag.startswith("#") else tag`. `removeprefix` says the same thing directly.
