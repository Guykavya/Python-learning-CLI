# total_ordering for playing cards

Writing all of `<`, `<=`, `>`, `>=` is boring. `functools.total_ordering` fills in the rest when you
give it `__eq__` and **one** of `__lt__`, `__le__`, `__gt__`, `__ge__`.

Write `Card(rank, suit)` in `solution.py`:

- `rank` is one of `"2" ... "10", "J", "Q", "K", "A"` (in that order, low to high).
- `suit` is one of `"clubs", "diamonds", "hearts", "spades"` (low to high).
- Anything else raises `ValueError` in `__init__`.
- Cards compare by rank first, then by suit. Use `@total_ordering` and write only `__eq__` and `__lt__`.
- Cards must be hashable and consistent with equality, so they work in sets.
- `repr(c)` is `Card('A', 'spades')`.
- Comparing with other types: `==` is `False`, `<` raises `TypeError`.

**Example**

```python
a, b = Card("10", "hearts"), Card("J", "clubs")
print(a < b, a >= b)                    # True False
print(Card("A", "clubs") > Card("A", "diamonds"))   # False
print(sorted([b, a])[0])                 # Card('10', 'hearts')
```
