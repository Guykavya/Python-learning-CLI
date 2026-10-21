## Hint 1

You need two counters: lines seen and lines kept. Which one increases for every line?

## Hint 2

After stripping, a blank line is `""` (falsy), and a comment line starts with `#`.

## Hint 3

```
total += 1
text = line.strip()
if not text or text.startswith("#"):
    continue
kept += 1
print(f"{kept}: {text}")
```
