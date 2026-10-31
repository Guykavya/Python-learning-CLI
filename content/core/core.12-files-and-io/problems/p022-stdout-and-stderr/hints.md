## Hint 1

Which argument of `print` chooses the stream? Which module has the stream objects?

## Hint 2

```
import sys
total = 0
for item in items:
    try: total += int(item)
    except ValueError: print(f"warning: skipping {item!r}", file=sys.stderr)
print(f"total: {total}")
return total
```
