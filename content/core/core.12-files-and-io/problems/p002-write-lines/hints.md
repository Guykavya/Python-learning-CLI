## Hint 1

`file.write()` writes exactly the text you give it. Does it add a newline for you? Which mode replaces old content?

## Hint 2

```
with open(path, "w", encoding="utf-8") as f:
    for line in lines:
        write line + newline
return len(lines)
```
`lines` could be a list, so `len(lines)` works. You may also use `writelines`, but it adds no newlines either.
