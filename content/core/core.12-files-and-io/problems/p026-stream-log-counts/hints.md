## Hint 1

What is the type of `f` after `with open(path) as f`? Can you use it directly in a `for` loop? And which
method of a string gives you the words of a line, and how do you get the third one safely?

## Hint 2

```
counts = {}
with open(path, encoding="utf-8") as f:
    for line in f:
        parts = line.split()
        if len(parts) < 3: continue
        level = parts[2]
        counts[level] = counts.get(level, 0) + 1
return counts
```
