## Hint 1

Work through the five rules one by one. Which Python tools give you "the items of a dict, sorted by key" and "is there any whitespace in this string"?

## Hint 2

```text
check namespace (non-empty str, no ':', no c.isspace())
kept = sorted((name, value) for name, value in params.items() if value is not None)
if not kept: return f"{namespace}:v{version}"
part = "&".join(f"{name}={value}" for name, value in kept)
if len(part) > 64 or any(c.isspace() for c in part):
    part = "sha256=" + hashlib.sha256(part.encode("utf-8")).hexdigest()
return f"{namespace}:v{version}:{part}"
```

Use `hashlib`, not Python's built-in `hash()`: `hash()` of a string changes every time Python starts.
