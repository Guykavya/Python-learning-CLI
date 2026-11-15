# Trace anagram grouping

This program groups words by a canonical key. Predict **exactly** what it prints. Do not run it.

```python
words = ["listen", "silent", "enlist", "google", "gogole", "cat", "act"]
groups = {}
for w in words:
    key = "".join(sorted(w))
    if key not in groups:
        groups[key] = []
    groups[key].append(w)
    print(w, key, len(groups[key]))
for key, g in groups.items():
    print(key, g)
print(sorted(len(g) for g in groups.values()))
counts = {}
for w in words:
    counts[len(w)] = counts.get(len(w), 0) + 1
print(counts)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Sort the letters of each word to get its key: `listen` becomes `eilnst`. Keep a table of key -> list of words.
In the first loop the printed number is the length of that key's list **after** the append. The final dictionary prints
in the order the keys were first created.

## After you answer

1. Which two words in the list look similar but are **not** anagrams? What differs?
2. Why can the sorted letters serve as a dictionary key although `sorted(w)` itself cannot?
3. What would `counts` look like if you grouped by word length instead of by key?
