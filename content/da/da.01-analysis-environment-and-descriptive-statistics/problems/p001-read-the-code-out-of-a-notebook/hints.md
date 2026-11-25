## Hint 1

What are the two shapes `cell["source"]` can have, and which Python test tells them apart? What happens if you call `"".join` on a plain string?

## Hint 2

```text
result = []
for cell in nb["cells"]:
    if cell["cell_type"] != "code": continue
    source = cell["source"]
    text = source if it is a str else "".join(source)
    result.append(text)
return result
```
