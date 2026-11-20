## Approach

Three layers, each small, all going through one function.

```text
models        Category, Item (quantity with CheckConstraint >= 0), Movement (an append-only history)
move_stock    @atomic: UPDATE ... SET quantity = quantity + delta (the database refuses < 0), then INSERT a Movement
admin         ItemAdmin (search, filter, read-only quantity), MovementAdmin (audit trail, no add/change/delete)
API           ReadOnlyModelViewSet + a "move" action for staff that calls move_stock; 409 on InsufficientStock
```

The finished file (the same one `learn validate` runs):

```python
from django.conf import settings
from django.contrib import admin
from django.db import IntegrityError, models, transaction
from django.db.models import F
from django.urls import include, path
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter


# --- models ---------------------------------------------------------------------------------------

class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=20, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "shop"
        ordering = ["name"]
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gte=0), name="item_quantity_gte_0")]

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Movement(models.Model):
    class Reason(models.TextChoices):
        RECEIVE = "receive", "Goods received"
        SALE = "sale", "Sale"
        ADJUST = "adjust", "Stock-take adjustment"

    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="movements")
    delta = models.IntegerField()
    reason = models.CharField(max_length=20, choices=Reason)
    note = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="+")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "shop"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.item.sku} {self.delta:+d} ({self.reason})"


# --- the one function that changes stock ----------------------------------------------------------

class InsufficientStock(Exception):
    pass


@transaction.atomic
def move_stock(item, delta, reason, user=None, note=""):
    if delta == 0:
        raise ValueError("A movement of zero units is meaningless.")
    try:
        with transaction.atomic():                       # a savepoint: the failed UPDATE must not poison the outer transaction
            Item.objects.filter(pk=item.pk).update(quantity=F("quantity") + delta)
    except IntegrityError:                               # the CheckConstraint (quantity >= 0) refused the new value
        item.refresh_from_db(fields=["quantity"])
        raise InsufficientStock(f"Cannot remove {-delta} of {item.sku}: only {item.quantity} in stock.")
    item.refresh_from_db(fields=["quantity"])
    return Movement.objects.create(item=item, delta=delta, reason=reason, note=note, created_by=user)


# --- admin ----------------------------------------------------------------------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "quantity")
    list_filter = ("category",)
    search_fields = ("name", "sku")
    readonly_fields = ("quantity",)                      # stock changes only through movements


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ("item", "delta", "reason", "created_by", "created")
    list_filter = ("reason",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# --- API ------------------------------------------------------------------------------------------

class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Item
        fields = ["id", "name", "sku", "category", "category_name", "price", "quantity"]
        read_only_fields = fields


class MoveSerializer(serializers.Serializer):
    delta = serializers.IntegerField()
    reason = serializers.ChoiceField(choices=Movement.Reason.choices)
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_delta(self, value):
        if value == 0:
            raise serializers.ValidationError("Delta must not be zero.")
        return value


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.select_related("category")
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def move(self, request, pk=None):
        item = self.get_object()
        serializer = MoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            movement = move_stock(item, data["delta"], data["reason"], user=request.user, note=data["note"])
        except InsufficientStock as error:
            return Response({"detail": str(error)}, status=status.HTTP_409_CONFLICT)
        body = {"id": movement.pk, "delta": movement.delta, "reason": movement.reason, "quantity": item.quantity}
        return Response(body, status=status.HTTP_201_CREATED)


router = DefaultRouter()
router.register("items", ItemViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
```

Why it is built this way:

- **One door.** Admin, API and scripts all change stock through `move_stock`, so the rule and the history live in one place (the idea of chapter section 9.3).
- **The database is the last line of defence.** `CheckConstraint(quantity__gte=0)` means even a bug or a raw `update()` cannot make stock negative: `IntegrityError`.
- **`F()` and the savepoint.** `quantity = quantity + delta` is computed by the database, so two requests do not overwrite each other. The inner `transaction.atomic()` is a savepoint: it lets us catch the `IntegrityError` and turn it into `InsufficientStock` without breaking the outer transaction.
- **Permissions come from Django.** The admin gives 403 or a redirect with no code of ours; the API uses `IsAuthenticated` for reading and `IsAdminUser` for `move`.

## The real migration flow (not run by the tests)

The tests build the tables with a schema editor because this exercise has no app folder. In the reference project (`docs/reference/swe.06-django-inventory/`) the model for movements was added like this (chapter section 18, step 1):

```bash
python manage.py makemigrations inventory     # writes inventory/migrations/0004_stockmovement.py
python manage.py migrate inventory            # runs it and records it in django_migrations
python manage.py makemigrations --check --dry-run    # in CI: fails if a model change has no migration file
```

Commit the migration file with the model change, and never edit one that a teammate or a server has already applied. The reference project's `python manage.py test` runs 25 tests in about 6 seconds.

## Before it goes live (remarks, from chapter sections 16.3 and 17.2)

- `python manage.py check --deploy` audits the settings. With the development settings the reference project prints one error (the console email backend, new in Django 6.1) and seven warnings (HSTS, SSL redirect, the generated `SECRET_KEY`, secure cookies, `DEBUG`, `ALLOWED_HOSTS`). The fix is a separate `prod_settings.py` that imports the base settings and overrides them, with secrets from environment variables; with it the check prints "System check identified no issues".
- A management command is the place for batch jobs that use the same rules: the reference project's `low_stock_report` (`BaseCommand`, `add_arguments`, `handle`, `CommandError`) prints the items at or below their reorder level. A CSV import command would call `move_stock` for each row instead of writing `quantity`.

## Complexity

`move_stock` is one UPDATE and one INSERT inside a transaction (a few statements, independent of the stock size). The API list is one query that joins the category; the admin changelist is a constant number of queries plus the page.

## Another way

Without the `CheckConstraint`, guard in the `UPDATE`: `Item.objects.filter(pk=item.pk, quantity__gte=-delta).update(...)` and treat "0 rows updated" as `InsufficientStock` (what the reference project does). That works on every database but depends on every code path remembering the filter; the constraint protects all of them. For high contention, `select_for_update()` locks the row first (PostgreSQL), and `TransactionTestCase` is needed to test two real concurrent sales.

## Not covered

Login and permission groups for a real warehouse team (Ch. 13), HTML pages for staff (Ch. 12), a `low_stock` queryset, pagination of the API and filtering, and running on a server. Try them as extensions on the full reference project.
