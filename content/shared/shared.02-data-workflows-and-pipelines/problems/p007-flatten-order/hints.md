## Hint 1

Do it one output key at a time. Which values come from `order["customer"]` instead of
`order`? What must happen to `city` *before* you call `.strip()` on it, given that it can be
`None`? After `datetime.fromisoformat(text)`, how can you tell whether the result has an
offset (look at `.tzinfo`)?

## Hint 2

```
def parse_utc(text, field):
    moment = datetime.fromisoformat(text)
    if moment.tzinfo is None: raise ValueError(f"{field}: no timezone")
    return moment.astimezone(timezone.utc)

city = customer["city"]
if city is not None: city = city.strip().title() or None     # "" or None -> None
return {"id": ..., "email": ...strip().lower(), "amount": Decimal(text), ...,
        "item_count": len(items), "total_qty": sum(i["qty"] for i in items)}
```
