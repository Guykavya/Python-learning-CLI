## Hint 1

For the median, which list do you need first, and how do you find the middle of an even-length list (two positions) versus an odd-length list (one)? For the mode, what is the first thing to count?

## Hint 2

```text
mean: sum(values) / len(values)
median: s = sorted(values); mid = len(s) // 2
        odd: s[mid]; even: (s[mid - 1] + s[mid]) / 2
modes: counts = {}; for v in values: counts[v] = counts.get(v, 0) + 1
       top = max(counts.values()); return sorted(v for v, c in counts.items() if c == top)
```
