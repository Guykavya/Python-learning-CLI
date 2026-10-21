## Approach

Do not delete from the list you are looping over. Build a new list of the words to keep. The
number removed is the difference in lengths.

## Code

```python
words = input().split()
target = input().strip()
kept = [w for w in words if w != target]
print(" ".join(kept) if kept else "(empty)")
print("Removed:", len(words) - len(kept))
```

## Complexity

One pass over n words: O(n). A loop of `while target in words: words.remove(target)` is also
correct, but each `in` and each `remove` scans the list, so it is O(n²) in the worst case.

## Another way

`removed = words.count(target)` then the comprehension. Or loop over a copy:
`for w in words[:]: if w == target: words.remove(w)`.
