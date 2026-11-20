# Computed fields and output names

Chapter sections 5.7 (`model_dump` and its filters), 5.10 (computed fields and aliases) and 7.1 (return annotation as the response model). The front-end team wants order totals computed by the server, the date under the camelCase name `createdAt`, and no `null` keys.

In `solution.py` define `app = FastAPI()` and:

```python
class Line(BaseModel):
    name: str
    price_paise: int = Field(ge=0)
    qty: int = Field(ge=1)
```

and a model `Order` with

- `items: list[Line]`
- `coupon: str | None = None`
- `created_at: datetime` that is **written out** as `createdAt`: `Field(serialization_alias="createdAt")`. (A *serialization* alias changes only the output name; clients still **send** `created_at`.)
- a `@computed_field` property `total_paise` (type `int`): the sum of `price_paise * qty` over the items.

Then:

1. `to_api(order: Order) -> dict` returns `order.model_dump(mode="json", by_alias=True, exclude_none=True)`: JSON-safe values (the date becomes a string), output names, and no keys whose value is `None`.
2. `POST /orders/preview` takes an `Order` body and returns it unchanged. Declare the response model with the return annotation `-> Order` and pass `response_model_exclude_none=True` to the decorator. FastAPI writes responses **by alias** by default, so the JSON has `createdAt` and the computed `total_paise`.

## Example

```text
POST /orders/preview
{"items": [{"name": "pen", "price_paise": 1050, "qty": 2},
           {"name": "book", "price_paise": 29900, "qty": 1}],
 "created_at": "2026-03-01T09:30:00"}
-> 200 {"items": [...same...], "createdAt": "2026-03-01T09:30:00", "total_paise": 32000}
        (no "coupon" key: it was None)

POST /orders/preview {"items": [], "createdAt": "2026-03-01T09:30:00"}
-> 422 ["body", "created_at"] missing      (the alias is for output only)
```
