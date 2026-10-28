## Hint 1

The order of the **folders** matters more than the kind of match. So the outer loop is over folders.
Inside one folder, which of the two paths do you test first?

## Hint 2

```
for folder in folders:
    base = Path(folder)
    if (base / name / "__init__.py").is_file(): return that path
    if (base / (name + ".py")).is_file(): return that path
return None
```

`is_file()` is simply `False` for a folder that does not exist, so no special case is needed.
