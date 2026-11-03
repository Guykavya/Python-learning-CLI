## Approach

Build a new dict, one key at a time, and give each value a real type:

- **Money as `Decimal`.** `float("0.10")` is really `0.1000000000000000055...`; add enough of
  them and the totals are off by paise. `Decimal("0.10")` is exact and keeps its scale
  (`"5.00"` stays `5.00`). That is also why the API sends the amount as a string: a JSON number
  would already be a float when parsed.
- **Timestamps as aware UTC `datetime`s.** `fromisoformat` reads both `Z` and `+05:30`. Converting
  everything to UTC means two rows can be compared and sorted directly, and `15:30+05:30` and
  `10:00Z` are recognised as the same moment. A timestamp without an offset is refused: guessing
  would shift some rows by 5.5 hours without any error.
- **Normalised strings.** `strip()` removes stray spaces, `lower()`/`upper()`/`title()` give one
  spelling per value, so `"Shipped"`, `"shipped "` and `"SHIPPED"` group together later. A blank
  city becomes `None`, so a null check finds it. `"   ".strip()` is `""`, and `"" or None` is `None`.
- **Nested to flat.** `customer.email` becomes `email`; the item list becomes two numbers.

Never changing the input matters: the raw record is what you quarantine or store in the raw
layer when something goes wrong later, so it must still be the original.

## Code

```python
from datetime import datetime, timezone
from decimal import Decimal


def parse_utc(text, field):
    moment = datetime.fromisoformat(text)
    if moment.tzinfo is None:
        raise ValueError(f"{field}: timestamp {text!r} has no timezone offset")
    return moment.astimezone(timezone.utc)


def flatten_order(order):
    customer = order["customer"]
    city = customer["city"]
    if city is not None:
        city = city.strip().title() or None
    items = order["items"]
    return {
        "id": order["id"],
        "email": customer["email"].strip().lower(),
        "city": city,
        "status": order["status"].strip().lower(),
        "amount": Decimal(order["amount"].strip()),
        "currency": order["currency"].strip().upper(),
        "created_at": parse_utc(order["created_at"], "created_at"),
        "updated_at": parse_utc(order["updated_at"], "updated_at"),
        "item_count": len(items),
        "total_qty": sum(item["qty"] for item in items),
    }
```

## Complexity

O(k) for `k` item lines; everything else is constant work per order.

## Another way

For many fields, a table of `field -> converter` keeps the code short and makes the rules easy
to review:

```python
CONVERT = {"status": lambda s: s.strip().lower(), "currency": lambda s: s.strip().upper(),
           "amount": lambda s: Decimal(s.strip())}
row = {key: CONVERT[key](order[key]) for key in CONVERT}
```

Then add the nested and computed fields by hand. Some teams store money as integer **cents**
(`1999`) instead of `Decimal`; that is exact too, and works in databases without a decimal
type, but you must know each currency's number of decimal places.
