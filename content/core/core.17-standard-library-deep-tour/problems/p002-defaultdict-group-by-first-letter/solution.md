## Approach

A `defaultdict(factory)` behaves like a dict, except that reading a **missing** key with `d[key]`
calls `factory()`, stores the result under that key and returns it. With `list` as the factory,
`groups[letter].append(word)` either appends to the existing list or to a new empty one: no
`if key not in groups` dance. With `int` as the factory the default is `0`, so `counts[n] += 1`
just works.

The last line of each function converts back with `dict(...)`. The defaultdict is a building
tool. Handing it to a caller is a trap: their innocent `result["z"]` would create a new empty entry
instead of telling them the key is missing.

## Code

```python
from collections import defaultdict


def group_by_first_letter(words: list[str]) -> dict[str, list[str]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for word in words:
        if word:
            groups[word[0].lower()].append(word)
    return dict(groups)


def count_by_length(words: list[str]) -> dict[int, int]:
    counts: defaultdict[int, int] = defaultdict(int)
    for word in words:
        counts[len(word)] += 1
    return dict(counts)
```

## Complexity

O(n) time for n words, O(n) extra space for the groups.

## Another way

With a plain dict, `groups.setdefault(key, []).append(word)` does the same in one line, and the
result is already a plain dict. The cost: `setdefault` builds a new empty list on every call,
even when the key exists. For counting, `collections.Counter(len(w) for w in words)` is the
most direct tool; `dict(Counter(...))` gives the plain dict.
