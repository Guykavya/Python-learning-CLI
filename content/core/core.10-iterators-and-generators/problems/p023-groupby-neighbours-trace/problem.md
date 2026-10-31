# Trace: groupby only joins neighbours

Predict the exact output. Pay attention to **which** words land in the same group, and to what
happens to group objects that are saved for later.

```python
from itertools import groupby

words = ["apple", "avocado", "banana", "apricot", "blueberry", "cherry"]
for letter, group in groupby(words, key=lambda w: w[0]):
    print(letter, list(group))

print("---")
for letter, group in groupby(sorted(words), key=lambda w: w[0]):
    print(letter, list(group))

print("---")
groups = groupby(sorted(words), key=lambda w: w[0])
saved = [(letter, group) for letter, group in groups]
for letter, group in saved:
    print(letter, list(group))
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
The program never stops with an error, so you never need to write a traceback.
