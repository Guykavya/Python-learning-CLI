# Trace a Counter

`collections.Counter` is a dictionary specialised for counting. Predict **exactly** what this program prints.
Do not run it.

```python
from collections import Counter

words = "to be or not to be that is the question to be".split()
c = Counter(words)
print(c)
print(c["be"], c["zzz"])
print(c.most_common(2))
c["or"] += 5
print(c.most_common(3))
print(len(c), sum(c.values()))
c.update(["is", "is"])
print(c["is"])
print("zzz" in c)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

First count the words by hand, in the order each first appears. `most_common(k)` lists the `k` biggest counts; items
with the **same count** stay in the order they were first inserted. `print(c)` shows
`Counter({'word': count, ...})` with the largest count first.

## After you answer

1. What does `c["zzz"]` return for a word that is not counted, and does it add the key?
2. Why does `len(c)` differ from `sum(c.values())`?
3. What did `update` do: add new keys, or add to counts?
