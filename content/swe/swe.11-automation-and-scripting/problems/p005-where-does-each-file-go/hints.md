## Hint 1

`Path(path).suffix` gives the last suffix with its dot. What does `.lower()` change for `".JPG"`? Which dictionary method returns a default instead of raising `KeyError`? For the second function: which `Path` method gives a new path with the same folder and a different name?

## Hint 2

```text
category_for: return CATEGORIES.get(Path(path).suffix.lower(), "other")
unique_destination:
    if not dst.exists(): return dst
    n = 1
    loop: candidate = dst.with_name(f"{dst.stem} ({n}){dst.suffix}")
          if not candidate.exists(): return candidate
          n += 1
```
