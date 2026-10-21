## Approach

Scan left to right. The moment a word is seen for the second time, that is the earliest second
occurrence of any word. A dict gives the first position in O(1).

## Code

```python
first_pos = {}
for i, word in enumerate(input().split(), start=1):
    if word in first_pos:
        print(f"{word} at {first_pos[word]} and {i}")
        break
    first_pos[word] = i
else:
    print("No repeats")
```

## Complexity

O(n) on average. With `if word in words[:i]` or a list of seen words, each check is O(n), so
the whole scan is O(n²): with 100,000 words that is billions of comparisons.

## Note on for-else

The `else` of a `for` loop runs only when the loop finished **without** `break`.
