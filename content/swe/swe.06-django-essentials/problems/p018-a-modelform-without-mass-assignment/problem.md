# A ModelForm without mass assignment

Chapter sections 11.1, 11.2 and "Try it: mass assignment". A form built from a model is a quick way to edit rows, and a quick way to let a visitor edit fields you never meant to show. The cure is an explicit allow-list.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`. Do not change a model while the tests run.

The starter has `Category` (`name`) and `Item` (`name`, `sku` unique, `price`, `quantity` default 0, `category`). Write `ItemForm`, a `ModelForm` for `Item`:

1. It has exactly the fields `name`, `sku`, `price`, `category`, in this order, chosen with `fields = [...]` (an allow-list, **not** `exclude`). `quantity` is not a form field: a POST that contains `quantity=999` must change nothing, for a new item (it keeps the default 0) and for an existing one (it keeps its stock).
2. `clean_sku` removes spaces around the value, converts it to upper case and checks the pattern **2 to 4 letters, a hyphen, 3 to 5 digits** (`AB-123`, `PEN-00042`). A value that does not match raises `forms.ValidationError`, so the error appears under `form.errors["sku"]`.
3. Because `clean_sku` runs before Django's uniqueness check, `"ab-123"` is refused when `AB-123` already exists (the error is on `sku` too).

## Example

```text
data: name=Pen sku=" ab-123 " price=1.50 category=<id> quantity=999
form.is_valid()  -> True
form.save()      -> Item(sku="AB-123", quantity=0)

sku="abc"        -> errors["sku"]
```
