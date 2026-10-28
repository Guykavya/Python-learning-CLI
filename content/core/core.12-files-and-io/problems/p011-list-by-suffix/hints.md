## Hint 1

`Path.iterdir()` gives all entries, files and folders. What do `is_file()` and `suffix` tell you? Is the order of `iterdir()` guaranteed?

## Hint 2

```
folder = Path(folder)
names = []
for item in folder.iterdir():
    if item.is_file() and item.suffix.lower() == suffix.lower():
        names.append(item.name)
return sorted(names)
```
