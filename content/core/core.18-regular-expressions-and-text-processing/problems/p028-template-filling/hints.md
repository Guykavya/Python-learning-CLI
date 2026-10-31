## Hint 1

The pattern needs literal braces. `{` is special in regex (`{2,3}`), so escape it: `\{\{`.
Capture the name with `([A-Za-z_]\w*)` and allow `\s*` on both sides. What should the
replacement be when the name is missing? (Hint: what is `m.group(0)`?)

## Hint 2

Why is a replacement **string** a bad idea here, even when you build it per name? Think about a
value like `C:\new\1`. A replacement **function**'s return value is used as it is, with no
backslash processing.

## Hint 3

```
PLACEHOLDER = \{\{\s*([A-Za-z_]\w*)\s*\}\}

def fill(m):
    name = m.group(1)
    if name in values: return str(values[name])
    return m.group(0)

return re.sub(PLACEHOLDER, fill, template)
```
