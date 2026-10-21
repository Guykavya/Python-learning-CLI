# Sort words with a lambda key

Write `sort_by_length(words)` that returns a **new** list of the words sorted:

1. by length, shortest first;
2. words of equal length alphabetically, **ignoring case**.

Use `sorted` with a `key=lambda ...` that returns a tuple. The input list must not change.

**Examples**

```python
sort_by_length(["banana", "Fig", "apple", "kiwi", "date"])
# ['Fig', 'date', 'kiwi', 'apple', 'banana']

sort_by_length(["bb", "B", "a", "AA"])
# ['a', 'B', 'AA', 'bb']
```
