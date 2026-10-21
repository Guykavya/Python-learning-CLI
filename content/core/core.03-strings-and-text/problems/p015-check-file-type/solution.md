## Code

```python
name = input()
print(f"Image: {name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))}")
print(f"Hidden: {name.startswith('.')}")
print(f"Backup: {name.endswith(('~', '.bak'))}")
```

## Why a tuple

`endswith` with a tuple returns `True` if any option matches. It is shorter and clearer than combining four calls with `or`.

## Why `lower()` only for the image check

The task says "in any case" only for images. Lowercasing first means you need just the lowercase options.

## Another way

`name.lower()[-4:] in (".png", ".jpg", ".gif")` works for three-letter extensions but breaks for `.jpeg`. `endswith` does not care about lengths.
