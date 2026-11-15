## Approach

Use `key=len`. The key function is called once per word, and sorting compares the keys. Because `sorted` is stable, words with equal keys stay in their original order.

## Code

```python
n = int(input())
words = input().split()
print(" ".join(sorted(words, key=len)))
```

## Complexity

O(n log n) time, O(n) memory.

## Another way

Bucket by length: make 21 lists, append every word to the list for its length, then concatenate the lists. This is O(n) and also stable (a tiny counting sort).
