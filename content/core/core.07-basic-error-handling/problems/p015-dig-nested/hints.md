## Hint 1

`{}["x"]` raises `KeyError`, `[][0]` raises `IndexError`. Which class in section 4's tree is the
parent of both?

## Hint 2

You can put the whole `for` loop inside one `try`: any step that fails ends the dig.

## Hint 3

```
try:
    for key in keys:
        data = data[key]
except LookupError:
    return default
return data
```
