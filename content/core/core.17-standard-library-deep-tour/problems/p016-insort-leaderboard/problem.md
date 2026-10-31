# bisect.insort: a leaderboard that stays sorted

A game shows the top players all the time. Sorting the whole list after every new score is
wasteful. `bisect.insort(a, x)` inserts `x` into an already sorted list at the right place, so the
list **stays** sorted, and bisect searches can then answer "what is my rank?" in O(log n).

The trick is the sort key. We want highest score first, and for equal scores the name in
alphabetical order. Store entries as tuples `(-score, name)`: tuples compare field by field, so
ascending `(-score, name)` means descending score, then ascending name.

Write a class `Leaderboard` in `solution.py`:

- `add(name: str, score: int)`: record a score. If the player already has a score, the **new**
  score **replaces** the old one (even if it is lower).
- `remove(name)`: remove the player; unknown name: `KeyError`.
- `top(n: int) -> list[tuple[str, int]]`: the first `n` players as `(name, score)`, highest score
  first, equal scores by name A→Z.
- `rank(name) -> int`: **competition ranking**: 1 + the number of players with a **strictly
  higher** score. Equal scores share a rank (scores 50, 40, 40, 30 have ranks 1, 2, 2, 4).
  Unknown name: `KeyError`.
- `count_at_least(score: int) -> int`: how many players have a score `>= score`.
- `__len__()`: the number of players.

Use `insort` to add and bisect functions to search; do not call `sort()` or `sorted()`.

**Example**

```python
lb = Leaderboard()
lb.add("cy", 40); lb.add("ana", 50); lb.add("bo", 40); lb.add("dee", 30)
lb.top(3)               # [('ana', 50), ('bo', 40), ('cy', 40)]
lb.rank("cy")           # 2   (only ana is strictly higher)
lb.rank("dee")          # 4
lb.count_at_least(40)   # 3
lb.add("dee", 60)       # replaces 30
lb.top(1)               # [('dee', 60)]
```
