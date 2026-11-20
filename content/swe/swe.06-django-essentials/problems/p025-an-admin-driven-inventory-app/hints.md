## Hint 1

Build in layers and run the tests after each one: 1) the models (the first failing test names the missing field), 2) `move_stock` (the model tests and the stock tests), 3) the admin, 4) the API. Which layer must exist before the others can be tested at all? Why is it good that the API and the admin both call `move_stock` and never touch `quantity` themselves?

## Hint 2

For `move_stock`: decorate it with `@transaction.atomic`. Update with `Item.objects.filter(pk=item.pk).update(quantity=F("quantity") + delta)` inside a small inner `with transaction.atomic():` (a savepoint), and catch `IntegrityError`: the `CheckConstraint` refused the new value, so refresh the item and raise `InsufficientStock`. Then `item.refresh_from_db(fields=["quantity"])` and `Movement.objects.create(...)`. For the admin: `readonly_fields`, `search_fields`, `list_filter`. For the API: `@action(detail=True, methods=["post"], permission_classes=[IsAdminUser])` on a `ReadOnlyModelViewSet`, a small plain `Serializer` for the input (`delta`, `reason`), and `select_related("category")` for the list.

## Hint 3

```text
move_stock: if delta == 0 -> ValueError
            try: (savepoint) UPDATE quantity = quantity + delta  except IntegrityError: refresh; raise InsufficientStock
            refresh item; return Movement.objects.create(item, delta, reason, note, created_by=user)
ItemAdmin: list_display, list_filter=("category",), search_fields=("name","sku"), readonly_fields=("quantity",)
MovementAdmin: has_add/change/delete_permission -> False
API: move(): validate -> try move_stock -> 201 {id, delta, reason, quantity}  except InsufficientStock -> 409
router.register("items", ItemViewSet); urlpatterns += path("api/", include(router.urls))
```
