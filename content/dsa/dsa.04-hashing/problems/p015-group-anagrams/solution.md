## Approach

A dictionary maps a canonical key to the list of words with that key. The key of a word is its sorted letters, which is
identical for all anagrams and different for non-anagrams. Then sort inside each group and sort the groups to get a
unique printable answer.

## Code

```python
n = int(input())
words = input().split()

groups = {}
for w in words:
    key = "".join(sorted(w))
    if key not in groups:
        groups[key] = []
    groups[key].append(w)

result = [sorted(g) for g in groups.values()]
result.sort(key=lambda g: g[0])
for g in result:
    print(*g)
```

## Complexity

O(n * L log L) for `n` words of length at most `L`: one sort per word. Dictionary work is O(n) on average.

## Another way

Use a **count tuple** as the key: 26 counts, one per letter. That costs O(L) per word instead of O(L log L) and gives the
same grouping. Comparing every pair of words with an anagram test is O(n^2 * L), much slower.

(`lambda` is only used for the sort key here: `key=lambda g: g[0]` means "sort by the first word".)
