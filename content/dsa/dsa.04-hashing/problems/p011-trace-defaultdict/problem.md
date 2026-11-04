# Trace defaultdict

A `defaultdict` creates a missing value the first time you read a key. That is convenient, and it hides a trap.
Predict **exactly** what this program prints. Do not run it.

```python
from collections import defaultdict

by_len = defaultdict(list)
for w in ["tea", "ate", "to", "at", "tan"]:
    by_len[len(w)].append(w)
    print(w, len(by_len))
print(dict(by_len))

total = defaultdict(int)
for ch in "mississippi":
    total[ch] += 1
print(dict(total))
print(total["z"], len(total))
print("q" in total, len(total))
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

For the first loop write the `by_len` dictionary after each word. `defaultdict(list)` gives an empty list for a new
key. For the second part, remember that **reading** `total["z"]` already creates the key `z` with value 0.

## After you answer

1. Why is `print(dict(...))` used instead of printing the defaultdict directly?
2. Which statement created the key `z`? How would `"z" in total` have avoided that?
3. When is `defaultdict` better than `.get(key, 0)`?
