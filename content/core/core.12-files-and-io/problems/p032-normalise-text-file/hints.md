## Hint 1

Which encoding name means "UTF-8, and drop a BOM at the start"? What does text mode do with `\r\n` when you read?
When you write, what does text mode do with `\n` on Windows, and which argument of `open` switches that off?

## Hint 2

```
with open(src, encoding="utf-8-sig") as f:
    text = f.read()
with open(dst, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
return len(text.splitlines())
```
