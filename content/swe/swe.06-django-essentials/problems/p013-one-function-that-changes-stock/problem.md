# One function that changes stock

Chapter sections 9.3 and 9.4, and project step 2. In the inventory project every stock change goes through **one** function, so the rules live in one place. Here you write that function and the two models it needs.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`. Do not change a model while the tests run.

In `solution.py` write:

- `Item`: `name` (`CharField`, max 50) and `quantity` (`IntegerField`, default 0). Its `Meta` has a `CheckConstraint` named `item_quantity_not_negative` that says `quantity >= 0`. (Django 6 spells it `models.CheckConstraint(condition=models.Q(...), name=...)`.)
- `Movement`: `item` (`ForeignKey` to `Item`, `on_delete=models.PROTECT`), `delta` (`IntegerField`), `reason` (`CharField`, max 20), `user` (`ForeignKey` to `settings.AUTH_USER_MODEL`, `null=True`, `blank=True`, `on_delete=models.SET_NULL`) and `created` (`DateTimeField(auto_now_add=True)`).
- `move_stock(item, delta, reason, user=None)`, which does all of this **or nothing**:
  1. `delta == 0` raises `ValueError` and writes nothing.
  2. It changes the stock **in the database**, with an `F()` expression (`quantity = quantity + delta` done by SQLite), not with `item.quantity += delta; item.save()`. Two copies of the same item in memory must not overwrite each other.
  3. It adds one `Movement` row (item, delta, reason, user).
  4. If the stock would go below 0 the database raises `IntegrityError` (that is the constraint's job: you do **not** write an `if` for it). Then the stock is unchanged **and no `Movement` row exists**.
  5. After a successful call `item.quantity` shows the new value, and the function returns the new `Movement`.

## Example

```text
item: pen, quantity 10
move_stock(pen, +5, "receive")   -> Movement(delta=5);  pen.quantity == 15
move_stock(pen, -20, "sale")     -> IntegrityError;     quantity still 15, no new Movement
move_stock(pen, 0, "adjust")     -> ValueError
```
