## Approach

Every word in an anagram group has the same **signature**: its letters in sorted order. Use
that signature as a dict key and group the words with `setdefault`.

## Code

```python
groups = {}
seen = set()
for word in input().split():
    if word in seen:
        continue
    seen.add(word)
    key = "".join(sorted(word))
    groups.setdefault(key, []).append(word)
if not groups:
    print("No words.")
for words in groups.values():
    print(" ".join(words))
```

## Complexity

For n words of length at most L: sorting each word is O(L log L), so the total is O(n L log L).

## Why a string key and not a list

`sorted(word)` returns a list, and lists cannot be dict keys. `"".join(...)` or `tuple(...)`
turns it into something hashable.
