## Hint 1

Handle the line in the order of the rules: cut at `#`, strip, skip empty and `-` lines, cut at `;`.
`text.split("#")[0]` or `text.partition("#")[0]` cuts at the first `#`. What is left looks like
`numpy >= 1.26 ` or `uvicorn[standard]~=0.29`.

## Hint 2

Walk with an index `i` while `line[i]` is a name character (`ch.isalnum() or ch in "-_."`). The name is
`line[:i]`, the rest is `line[i:]`. If the rest (after stripping) starts with `[`, cut everything up to
and including `]`.

## Hint 3

```
result = []
for raw in file lines:
    line = raw.partition("#")[0].strip()
    if not line or line.startswith("-"): continue
    line = line.partition(";")[0].strip()
    i = 0
    while i < len(line) and (line[i].isalnum() or line[i] in "-_."): i += 1
    name = line[:i].lower().replace("_", "-").replace(".", "-")
    rest = line[i:].strip()
    if rest.startswith("["): rest = rest.partition("]")[2]
    spec = rest.replace(" ", "")
    result.append((name, spec))
return result
```
