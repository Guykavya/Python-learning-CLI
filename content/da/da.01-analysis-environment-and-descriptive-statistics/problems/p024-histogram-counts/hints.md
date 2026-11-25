## Hint 1

How do you turn a value into a bin number with one formula? What happens to the maximum value with that formula, and how do you rescue it?

## Hint 2

```text
width = (high - low) / bins
for x in values:
    if x < low or x > high: outside += 1; continue
    i = 0 if width == 0 else int((x - low) / width)
    if i == bins: i = bins - 1          # the maximum
    counts[i] += 1
rows = [(low + i*width, low + (i+1)*width, counts[i]) ...]   (make the last right edge exactly high)
```
