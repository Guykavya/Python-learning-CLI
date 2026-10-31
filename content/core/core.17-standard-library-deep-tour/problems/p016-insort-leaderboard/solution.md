## Approach

The board keeps a list of `(-score, name)` tuples in ascending order. Negating the score turns
"highest first" into "smallest first", and the name then breaks ties alphabetically. `insort`
puts each new tuple in its place (binary search for the position, then a list insert), so the
list is always sorted and `top(n)` is just a slice.

A dict `name -> score` remembers each player's current score. That is needed to **find and
delete** the old tuple when the score changes: `bisect_left(entries, (-old, name))` lands exactly
on it because the tuple is unique.

Ranking uses bisect with `key=` (Python 3.10+), which compares only the first field:

- `bisect_left(entries, -score, key=first)` = number of entries with `-s < -score`, that is
  `s > score`: the players strictly ahead. Add 1 for the rank.
- `bisect_right(entries, -score, key=first)` = number with `-s <= -score`, that is `s >= score`.

## Code

```python
from bisect import bisect_left, bisect_right, insort


def _first(entry: tuple[int, str]) -> int:
    return entry[0]


class Leaderboard:
    def __init__(self) -> None:
        self._entries: list[tuple[int, str]] = []
        self._scores: dict[str, int] = {}

    def add(self, name: str, score: int) -> None:
        if name in self._scores:
            self.remove(name)
        self._scores[name] = score
        insort(self._entries, (-score, name))

    def remove(self, name: str) -> None:
        old = self._scores.pop(name)
        index = bisect_left(self._entries, (-old, name))
        del self._entries[index]

    def top(self, n: int) -> list[tuple[str, int]]:
        if n <= 0:
            return []
        return [(name, -neg) for neg, name in self._entries[:n]]

    def rank(self, name: str) -> int:
        score = self._scores[name]
        return bisect_left(self._entries, -score, key=_first) + 1

    def count_at_least(self, score: int) -> int:
        return bisect_right(self._entries, -score, key=_first)

    def __len__(self) -> int:
        return len(self._entries)
```

## Complexity

`rank`, `count_at_least`: O(log n). `add` and `remove`: O(log n) to find the spot plus O(n) to
shift list items on insert/delete (a fast memory move in practice). `top(k)`: O(k).

## Another way

Without `key=`, you can search with a tuple: players strictly ahead are the entries
`< (-score, "")` (the empty string is smaller than every name), so
`bisect_left(entries, (-score, ""))` works on older Pythons. For very large boards, the
third-party `sortedcontainers.SortedList` gives O(log n) inserts and deletes; the standard library
version above is plenty for thousands of players.
