## Approach

`sorted` with different keys. The sort is stable, and `reverse=True` keeps that stability, so
tied words stay in input order in every line.

## Code

```python
words = input().split()
print("Plain:", " ".join(sorted(words)))
print("Ignoring case:", " ".join(sorted(words, key=str.lower)))
print("By length:", " ".join(sorted(words, key=len)))
print("Longest first:", " ".join(sorted(words, key=len, reverse=True)))
```

## Complexity

Each sort is O(n log n). The key function is called once per word.

## Why not `[::-1]`

`sorted(words, key=len)[::-1]` puts the longest first, but it also reverses the order of tied
words. In the example, `pear kiwi date` would come out as `date kiwi pear`.
