## Hint 1

`defaultdict(list)` calls `list()` to make a value the first time a missing key is **read**. So
`groups[key].append(word)` works even for a brand-new key. Which factory gives you a fresh `0`
for counting?

## Hint 2

`int()` returns `0`, so `defaultdict(int)` lets you write `counts[n] += 1`. At the end, turn the
defaultdict into a plain dict with `dict(groups)`. Why does that matter for a caller who writes
`result["z"]`?

## Hint 3

```
group_by_first_letter(words):
    groups = defaultdict(list)
    for w in words:
        if w: groups[w[0].lower()].append(w)
    return dict(groups)

count_by_length(words):
    counts = defaultdict(int)
    for w in words: counts[len(w)] += 1
    return dict(counts)
```
