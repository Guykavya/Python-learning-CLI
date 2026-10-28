## Hint 1

Mode `"w"` wipes the file. Which mode keeps old content and also creates a missing file?

## Hint 2

```
with open(path, "a", encoding="utf-8") as f:
    f.write(text + "\n")
```
