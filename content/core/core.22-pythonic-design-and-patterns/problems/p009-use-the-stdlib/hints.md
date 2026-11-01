## Hint 1

Find the one-line description of each function: "count things", "group things by a key",
"first in, first out", "runs of equal items", "put lists end to end", "do not compute the same
thing twice". Which standard-library name matches each description? `Counter(...)` takes any
iterable. What does `groupby` need about the order of the input?

## Hint 2

```
word_counts     : Counter(text.lower().split())
top_words       : word_counts(text).most_common(n)
group_by_length : groups = defaultdict(list); for w in words: groups[len(w)].append(w)
bfs_order       : queue = deque([start]); queue.popleft(); seen as a set
run_lengths     : [(key, len(list(group))) for key, group in groupby(items)]
join_all        : list(chain(*lists))
count_paths     : put @cache above the def (from functools import cache)
```
`seen` should be a **set** (fast `in`); a list makes the search O(n) per check.
