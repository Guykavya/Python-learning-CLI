# A bounded TypeVar: the longest item

You want a function `longest` that works on a list of strings, a list of lists, a list of
tuples... and returns an item of the **same type** as the items. But it can only work if every
item has a `len()`. A plain `T` would say "anything", and then `len(item)` is an error in the
type checker. A **bound** says "any type, as long as it is at least a `Sized`":

```python
S = TypeVar("S", bound=Sized)
```

`Sized` (from `collections.abc`) is the protocol-like ABC of objects that have `__len__`.

Write in `solution.py`, using such a bounded TypeVar `S` for all three:

1. `longest(items: Iterable[S]) -> S`: the item with the largest `len`. If two items tie, return
   the **first** of them. An empty iterable raises `ValueError("longest() of empty iterable")`.
2. `shortest(items: Iterable[S]) -> S`: the item with the smallest `len`. Ties: the first. Empty:
   `ValueError("shortest() of empty iterable")`.
3. `longest_or_none(items: Iterable[S]) -> S | None`: like `longest`, but `None` for an empty input.

The tests check `S.__bound__`: the TypeVar in your hints must be bounded by `Sized` (or by a
more specific class that is a `Sized`, like `Collection` or `Sequence`).
On Python 3.12+ you may write `def longest[S: Sized](items: Iterable[S]) -> S:`.

**Examples**

```python
longest(["a", "abc", "ab"])      # 'abc'     a type checker says: str
longest([[1], [2, 3], [4, 5]])   # [2, 3]    ties: the first one wins
shortest(["bb", "a", "c"])       # 'a'
longest_or_none([])              # None
longest(iter(["xy", "z"]))       # 'xy'      an Iterable that is not a list works too
```
