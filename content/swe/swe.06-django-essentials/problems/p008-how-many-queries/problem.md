# How many queries?

Chapter section 6.6 and "Try it: how many queries?". A QuerySet is lazy: building it costs nothing, and the first time it is *used* it runs SQL and keeps its rows in a cache. Some methods use that cache, some ask the database again.

Below, eight lines run inside `CaptureQueriesContext`, which counts every SQL statement sent to the database since it started. After each line the program prints the **cumulative** number of queries (the total so far, not the number caused by that line alone). The four rows are created *before* the counting starts, so they are not counted. Everything above the `with` block is plumbing (a fake app and a table); the model is `Item`, ordered by name.

For every line decide: does it send SQL right now? If the QuerySet already holds its rows, can the method answer from them?

```python
import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):          # plumbing: a fake app "shop" so that the model has a home
    name = "__main__"
    label = "shop"


settings.configure(
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    INSTALLED_APPS=["__main__.ShopConfig"],
)
django.setup()

from django.db import connection, models
from django.test.utils import CaptureQueriesContext


class Item(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        app_label = "shop"
        ordering = ["name"]


with connection.schema_editor() as editor:
    editor.create_model(Item)
for name, quantity, price in [("Cable", 5, "3.50"), ("Hub", 0, "21.00"), ("Mouse", 7, "9.00"), ("Pad", 2, "4.00")]:
    Item.objects.create(name=name, quantity=quantity, price=price)

with CaptureQueriesContext(connection) as ctx:
    qs = Item.objects.filter(quantity__gt=0)
    print("1:", len(ctx))
    top = qs.order_by("-price")[:2]
    print("2:", len(ctx))
    total = qs.count()
    print("3:", len(ctx))
    names = [item.name for item in qs]
    print("4:", len(ctx))
    names_again = [item.name for item in qs]
    print("5:", len(ctx))
    size = len(qs)
    print("6:", len(ctx))
    empty = Item.objects.filter(quantity=0).exists()
    print("7:", len(ctx))
    cheapest = qs.first()
    print("8:", len(ctx))
```

Write your answer in `answer.txt`: eight lines, `1: ...` to `8: ...`, in the format of the `print` calls (for example `1: 0`). Do not run it.

## After you answer

1. Lines 4 and 5 loop over the same `qs`. Why does only the first one reach the database?
2. Line 3 (`count()`) and line 6 (`len()`) both give the number of rows. Why does one add a query and the other not? Which is cheaper on a table with a million rows when nothing is loaded yet?
3. Line 7 builds a *new* QuerySet. Why can it not use the cache of `qs`?
