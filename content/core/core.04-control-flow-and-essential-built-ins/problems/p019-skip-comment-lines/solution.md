## Approach

A loop-and-a-half reads until `END`. `continue` filters out unwanted lines at the top, so the
main work is not buried inside an `if`.

## Code

```python
total = 0
kept = 0
while True:
    line = input()
    if line == "END":
        break
    total += 1
    text = line.strip()
    if not text or text.startswith("#"):
        continue
    kept += 1
    print(f"{kept}: {text}")
print(f"Kept {kept} of {total} lines")
```

## Why count `total` before `continue`

`continue` skips everything below it. If `total += 1` came after it, skipped lines would not
be counted.

## Another way

Without `continue`: `if text and not text.startswith("#"): kept += 1; print(...)`. Fine for one
filter; with several filters, early `continue`s read better.
