## Hint 1

How do you loop over the lines of `sys.stdin`? Which module attribute is replaced when a test (or a shell pipe) provides different input: the name `sys` or the name `stdin` you imported?

## Hint 2

```
import sys
total = 0
for line in sys.stdin:
    line = line.strip()
    if line == "": continue
    total += int(line)
print(f"total: {total}")
return total
```
