# Two gifts that use the whole budget

You have a gift card and want to buy **two different** items that together cost **exactly**
the card's value.

Write `gift_pairs(items, budget)` in `solution.py`. `items` is a list of `(name, price)`
tuples. Return a **list** of `(name1, name2)` tuples for every pair of two different items
whose prices add up to `budget`.

- Never pair an item with itself (even if twice its price is the budget).
- `name1` is the item that comes **earlier** in `items`.
- Pairs are listed in the order `itertools.combinations(items, 2)` gives them.

**Example**

```python
items = [("pen", 20), ("book", 50), ("mug", 30), ("cap", 30), ("bag", 70)]
gift_pairs(items, 50)    # [('pen', 'mug'), ('pen', 'cap')]
gift_pairs(items, 100)   # [('mug', 'bag'), ('cap', 'bag')]    not ('book', 'book')
gift_pairs(items, 5)     # []
```
