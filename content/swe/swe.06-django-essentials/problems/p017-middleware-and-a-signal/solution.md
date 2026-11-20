## Approach

```python
VALID_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class RequestIDMiddleware:
    def __init__(self, get_response):          # runs once, at server start
        self.get_response = get_response

    def __call__(self, request):               # runs for every request
        incoming = request.headers.get("X-Request-ID", "")
        request.request_id = incoming if VALID_ID.match(incoming) else uuid.uuid4().hex
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response


@receiver(pre_save, sender=Item)
def remember_old_quantity(sender, instance, **kwargs):
    old = None
    if instance.pk:
        old = Item.objects.filter(pk=instance.pk).values_list("quantity", flat=True).first()
    instance._was_low = old is not None and old < instance.threshold


@receiver(post_save, sender=Item)
def alert_on_crossing(sender, instance, created, **kwargs):
    if instance.quantity < instance.threshold and not instance._was_low:
        LowStockAlert.objects.create(item=instance, quantity=instance.quantity)
```

**Middleware.** The request goes inward through the list, so code before `get_response(request)` sees the request and code after it sees the response. Because the middleware wraps everything below it, it also decorates a 404 (the URL resolver is below the middleware). `X-Request-ID` comes from outside, so it is validated: otherwise a client could put newlines or a huge string into your logs (log injection).

**Signal.** A crossing is a change of state, so the receiver must know two states: before and after. `post_save` only shows the after, so a `pre_save` receiver reads the database row, which still holds the before value, and stores one boolean on the instance. The rule "alert only on the way from `>= threshold` to `< threshold`" gives, for threshold 5 and saves 10, 7, 4, 3, 4, 0, 5, 4, 9, the alerts at the saves `4` and the second `4` (after the 5): two alerts. A rule "alert whenever quantity < threshold" would give five.

- A new item has no `pk` before its first save, so `old` is `None` and `_was_low` is `False`: an item born low raises one alert.
- Signals are connected when the module with the receivers is imported. In a real project you import them in `AppConfig.ready()`.
- Signals fire from `save()` and `delete()`. `Item.objects.filter(...).update(quantity=0)` and `bulk_create` skip them, so no alert would be written. That is why the project of Chapter 18 keeps stock rules in one explicit function (`record_movement`) and uses signals only for side effects.

## Complexity

The middleware does O(1) work per request. The `pre_save` receiver costs one extra `SELECT` per save; the alert costs one `INSERT` only on a crossing.

## Another way

Remember the old value without a query: override `Item.from_db` (or `__init__`) to store `self._loaded_quantity`, and update it after saving. That saves the `SELECT`, but a stale in-memory copy then compares against the wrong "before". Even simpler and safer: do not use a signal; write `def set_quantity(item, q)` that checks the crossing and creates the alert, and call it from every place that changes stock (explicit is easier to test).
