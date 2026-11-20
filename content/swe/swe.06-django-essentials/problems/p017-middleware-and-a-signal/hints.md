## Hint 1

Middleware: what runs once when the server starts (`__init__`) and what runs for each request (`__call__`)? Where must the id be created, and on which object do you set the header? For the signal: when `post_save` runs, the new value is already saved. How can you still know what the quantity was **before** this save?

## Hint 2

In `__call__`: read `request.headers.get("X-Request-ID", "")`, check it with a regular expression `^[A-Za-z0-9_-]{1,64}$`, otherwise `uuid.uuid4().hex`; set `request.request_id`; call `self.get_response(request)`; set `response["X-Request-ID"]`; return the response. For the signal, a `pre_save` receiver can read the old quantity from the database (`Item.objects.filter(pk=instance.pk).values_list("quantity", flat=True).first()`; a new item has no pk yet) and keep "was it low?" on the instance, for example `instance._was_low`. The `post_save` receiver creates the alert only if "is low now" and not "was low before".

## Hint 3

```text
pre_save(Item):  old = quantity in the database for instance.pk (None if new)
                 instance._was_low = old is not None and old < instance.threshold
post_save(Item): if instance.quantity < instance.threshold and not instance._was_low:
                     LowStockAlert.objects.create(item=instance, quantity=instance.quantity)
```

Trace for threshold 5: 10, 7 (not low), 4 (low, was not -> alert), 3 (was low -> no), 4 (no), 0 (no), 5 (not low), 4 (low, was not -> alert), 9.
