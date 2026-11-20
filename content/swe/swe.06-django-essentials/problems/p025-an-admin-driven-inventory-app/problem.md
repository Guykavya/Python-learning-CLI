# An admin-driven inventory app

The project of the module (chapter section 18). You build the heart of the inventory app in **one file**: models, one function that changes stock, an admin, and a small JSON API. The rules are the ones of the chapter: stock is never negative, and every change of stock leaves a record (a *movement*).

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`; do not change a model while tests run. Because there are no migration files here, `solution.md` shows the real `makemigrations` flow of the full project. Do not add inlines to `ItemAdmin` (the tests post the change form by hand). The starter has all the names the tests import; fill them in.

## Models

| Model | Fields |
|---|---|
| `Category` | `name` (unique); `__str__` returns the name |
| `Item` | `name`, `sku` (unique), `category` (FK to `Category`, `PROTECT`, `related_name="items"`), `price` (`DecimalField(8, 2)`), `quantity` (`IntegerField`, default 0); a `CheckConstraint(condition=Q(quantity__gte=0), name="item_quantity_gte_0")`; `__str__` |
| `Movement` | `item` (FK, `PROTECT`, `related_name="movements"`), `delta` (`IntegerField`), `reason` (choices `receive`, `sale`, `adjust`; the starter has `Movement.Reason`), `note` (blank allowed), `created_by` (FK to the user, null allowed, `SET_NULL`, `related_name="+"`), `created` (`auto_now_add`); `__str__` |

## `move_stock(item, delta, reason, user=None, note="")`

The only place that changes `Item.quantity`.

- It runs in **one transaction**: either both the new quantity and the `Movement` row are saved, or nothing is.
- The new quantity is computed **in the database** with `F("quantity") + delta` (the `item` object you were given may be out of date).
- If the new quantity would be below zero, it raises `InsufficientStock` (the starter defines the class) and changes nothing. The `CheckConstraint` is what really refuses it.
- `delta == 0` raises `ValueError`.
- After a success, `item.quantity` shows the new value, and the function **returns the new `Movement`** (with `created_by=user`).

## Admin (`/admin/`, `path("admin/", admin.site.urls)` is in the starter)

- `ItemAdmin`: `list_display` with name, sku, category, price and quantity; `list_filter` by category; `search_fields` name and sku (the search box is `?q=`); **`readonly_fields = ("quantity",)`**, so stock is changed only through movements.
- `MovementAdmin`: an audit trail: it can be listed, but nobody may add, change or delete a row (the three `has_..._permission` methods return `False`).
- `CategoryAdmin` registered.
- Staff users follow Django's permissions: no permission gives 403, a staff user with only `view_item` can see the list but cannot change an item (403). Django does this for you.

## API (`/api/`, a `DefaultRouter`)

| Request | Who | Answer |
|---|---|---|
| `GET /api/items/` and `GET /api/items/<pk>/` | logged-in users (`IsAuthenticated`) | 200; fields `id`, `name`, `sku`, `category`, `category_name`, `price`, `quantity`, all read-only. The list is a plain JSON list (no pagination) and takes **at most 2 queries**. |
| `POST /api/items/<pk>/move/` | **staff** only (`IsAdminUser`) | body `{"delta": -4, "reason": "sale", "note": "..."}` (`note` optional). 201 with `{"id", "delta", "reason", "quantity"}` (the **new** stock). 400 with the field name as key for a bad `delta` (zero or not an integer) or an unknown `reason`; 409 `{"detail": ...}` for not enough stock; 404 for an unknown item. A non-staff user gets 403, an anonymous user 403. |

Items cannot be written through the API (it is a `ReadOnlyModelViewSet`: stock changes only through `move`).

## Example

```text
Item "Zebra cable", quantity 10
POST /api/items/1/move/ {"delta": -4, "reason": "sale"}   (as staff)  -> 201 {"id": 1, "delta": -4, "reason": "sale", "quantity": 6}
POST /api/items/1/move/ {"delta": -11, "reason": "sale"}              -> 409, quantity still 6, no new Movement
POST /api/items/1/move/ {"delta": 0, "reason": "sale"}                -> 400 {"delta": [...]}
```
