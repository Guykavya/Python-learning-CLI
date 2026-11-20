# Fix the N+1 on the stock page

Chapter section 7.4. The page `/stock/` of the inventory app answers with JSON: every item with its category name and its tag names. It gives the right answer, but it is slow: for 40 items it sends 81 SQL queries (1 for the items, then 2 more **per item**: one for its category, one for its tags). On a real page with 2,000 items the database is the bottleneck.

In `solution.py` the models (`Category`, `Tag`, `Item`) and the view `stock_page` are already written, and the view is wired to `/stock/`. **Do not change the models and do not change the JSON**; change only the query inside `stock_page` so that the page costs a **constant number of queries**, at most 3, whatever the number of items.

Reminders: a forward `ForeignKey` (`item.category`) is fetched in the same query with `select_related`; a many-to-many (`item.tags`) needs a second query with `prefetch_related`. Loop over `item.tags.all()` (not `item.tags.order_by(...)` or `.filter(...)`: a new query ignores the prefetch). `Tag` already has a default ordering by name.

The JSON looks like this (items sorted by name, tags sorted by name):

```json
{"count": 2, "items": [
  {"name": "Item 00", "category": "Cables", "tags": ["new", "sale"]},
  {"name": "Item 01", "category": "Audio",  "tags": []}
]}
```

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models); every model needs `class Meta: app_label = "shop"`; do not change a model while tests run.
