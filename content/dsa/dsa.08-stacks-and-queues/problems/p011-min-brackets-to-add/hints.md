## Hint 1

Walk left to right with `open_count`. A `(` increases it. What should a `)` do when `open_count > 0`, and what when it is 0?

## Hint 2

```
opens = 0; open_count = 0
for ch in s:
    if ch == "(": open_count += 1
    elif open_count: open_count -= 1
    else: opens += 1            # a ) with nothing to close
return (opens, open_count)      # each still-open ( needs a )
```
