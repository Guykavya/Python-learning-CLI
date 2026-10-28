## Approach

Reading with `utf-8-sig` removes the BOM. The default `newline=None` in read mode translates `\r\n`, `\r` and
`\n` to `\n`, so the text in memory is clean. When writing, `newline="\n"` stops the translation of `\n`
to the system line ending, so the bytes are the same on every computer. Writing plain `"utf-8"` adds no BOM.

## Code

```python
def normalise_text_file(src, dst):
    with open(src, encoding="utf-8-sig") as f:
        text = f.read()
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return len(text.splitlines())
```

## Complexity

O(file size) time and memory. For huge files, loop over lines and write each line instead.

## Another way

Work with bytes: `data = src.read_bytes()`, remove the BOM with `data.removeprefix(b"\xef\xbb\xbf")`, and use
`replace(b"\r\n", b"\n").replace(b"\r", b"\n")`. The order of the two replaces matters.
