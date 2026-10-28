## Approach

Open the file once and loop over it. Each step of the loop gives one line, so the memory use stays small
whatever the size of the file. Split the line into words, skip lines with fewer than three words, and count
`parts[2]` in a dict with `counts.get(level, 0) + 1`.

## Code

```python
def count_levels(path):
    counts = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            level = parts[2]
            counts[level] = counts.get(level, 0) + 1
    return counts
```

## Complexity

Time O(total characters). Memory O(length of the longest line + number of different levels).

## Another way

`collections.Counter(parts[2] for ...)` with a generator expression does the same in fewer lines.
Use `line.split(None, 3)` to avoid splitting a very long message into many words.
