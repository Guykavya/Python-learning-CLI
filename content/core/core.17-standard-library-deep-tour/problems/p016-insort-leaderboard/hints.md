## Hint 1

Keep two things: a sorted list `self._entries` of `(-score, name)` tuples, and a dict `self._scores` from name to current score. Why do you need the dict? Think about `add` for a player who already has a score: what must happen to their old tuple first?

## Hint 2

To delete the old tuple, find it with `i = bisect_left(self._entries, (-old, name))` and `del self._entries[i]`. For `rank`, the players with a strictly higher score are the entries whose first field is `< -score`. `bisect_left(self._entries, -score, key=lambda e: e[0])` counts them (the `key=` argument of bisect needs Python 3.10+). `count_at_least` is the same idea with `bisect_right`.

## Hint 3

```
add(name, score):
    if name in scores: remove(name)
    scores[name] = score
    insort(entries, (-score, name))

remove(name):
    old = scores.pop(name)              # KeyError for free
    i = bisect_left(entries, (-old, name)); del entries[i]

top(n):            [(name, -neg) for neg, name in entries[:max(n, 0)]]
rank(name):        bisect_left(entries, -scores[name], key=first) + 1
count_at_least(s): bisect_right(entries, -s, key=first)
```
