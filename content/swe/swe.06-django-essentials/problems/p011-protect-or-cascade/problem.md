# PROTECT or CASCADE?

Chapter section 7.1 and "Try it: PROTECT or CASCADE?". The `on_delete` option of a `ForeignKey` decides what happens to the rows that point at a row you delete:

- `CASCADE`: delete them too.
- `PROTECT`: refuse the delete (Django raises `ProtectedError` and changes nothing).
- `SET_NULL`: keep them and set the foreign key to `NULL` (needs `null=True`).

Below are four models and five deletes, one after the other, in the same database (an earlier delete stays done). After each delete the program prints either `deleted` or `ProtectedError`, then the row counts. `no_supplier` counts the items whose `supplier` is `NULL`. Everything before the `attempt(...)` lines is plumbing; the starting data is: suppliers A and B; categories Cables and Tools; items Cable (Cables, supplier A), Hub (Cables, supplier B), Drill (Tools, supplier A); movements: 2 for Cable, 1 for Hub, 3 for Drill.

Work out the five output lines **on paper**: at each step, which rows disappear, which are refused, and which keep living with a `NULL`?

```python
import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):          # plumbing: a fake app "shop" so that the models have a home
    name = "__main__"
    label = "shop"


settings.configure(
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    INSTALLED_APPS=["__main__.ShopConfig"],
)
django.setup()

from django.db import connection, models
from django.db.models import ProtectedError


class Supplier(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        app_label = "shop"


class Category(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        app_label = "shop"


class Item(models.Model):
    name = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = "shop"


class Movement(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    delta = models.IntegerField()

    class Meta:
        app_label = "shop"


with connection.schema_editor() as editor:
    for model in (Supplier, Category, Item, Movement):
        editor.create_model(model)

supplier_a = Supplier.objects.create(name="A")
supplier_b = Supplier.objects.create(name="B")
cables = Category.objects.create(name="Cables")
tools = Category.objects.create(name="Tools")
cable = Item.objects.create(name="Cable", category=cables, supplier=supplier_a)
hub = Item.objects.create(name="Hub", category=cables, supplier=supplier_b)
drill = Item.objects.create(name="Drill", category=tools, supplier=supplier_a)
for item, how_many in [(cable, 2), (hub, 1), (drill, 3)]:
    for _ in range(how_many):
        Movement.objects.create(item=item, delta=1)


def state():
    return (
        f"categories={Category.objects.count()} suppliers={Supplier.objects.count()} "
        f"items={Item.objects.count()} movements={Movement.objects.count()} "
        f"no_supplier={Item.objects.filter(supplier=None).count()}"
    )


def attempt(number, what):
    try:
        what.delete()
        result = "deleted"
    except ProtectedError:
        result = "ProtectedError"
    print(f"{number}: {result} {state()}")


attempt(1, hub)
attempt(2, cables)
attempt(3, supplier_a)
attempt(4, cable)
attempt(5, cables)
```

Write your answer in `answer.txt`: five lines, `1: ...` to `5: ...`, in the format of the `print` in `attempt` (for example `1: deleted categories=2 suppliers=2 ...`, with the five counts in that order). Do not run it.

## After you answer

1. Step 2 is refused. Which model has the `PROTECT` that stops it, and what would have happened to Cable if `category` were `CASCADE`?
2. Step 3 deletes a supplier but no item is lost. Where do Cable and Drill point afterwards, and what must be true of the field for this to be allowed?
3. A product that was ever sold has order lines pointing at it. Which `on_delete` do you choose for that link, and why?
