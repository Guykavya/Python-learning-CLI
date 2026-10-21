## Approach

`max(words, key=len)` and `min(words, key=len)`. They compare by length and return the word.

## Code

```python
words = input().split()
if not words:
    print("No words")
else:
    longest = max(words, key=len)
    shortest = min(words, key=len)
    for label, word in (("Longest", longest), ("Shortest", shortest)):
        unit = "letter" if len(word) == 1 else "letters"
        print(f"{label}: {word} ({len(word)} {unit})")
```

## Why ties need no code

`max` only replaces its current best when a later item is **strictly** greater. So the first
of several equal items stays.

## Another way

`max(words, key=len, default=None)` and test for `None` instead of testing `words` first.
