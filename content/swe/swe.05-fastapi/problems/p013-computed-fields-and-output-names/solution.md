## Approach

Let the model describe its own output: a computed field for the total, a serialization alias for the date, and the dump switches for JSON values and missing keys.

```python
class Order(BaseModel):
    items: list[Line]
    coupon: str | None = None
    created_at: datetime = Field(serialization_alias="createdAt")

    @computed_field
    @property
    def total_paise(self) -> int:
        return sum(line.price_paise * line.qty for line in self.items)


def to_api(order: Order) -> dict:
    return order.model_dump(mode="json", by_alias=True, exclude_none=True)


@app.post("/orders/preview", response_model_exclude_none=True)
def preview(order: Order) -> Order:
    return order
```

Example: the two lines give `1050 * 2 + 29900 * 1 = 32000`. `model_dump()` gives `created_at` as a `datetime` and `coupon: None`; `to_api` gives `"createdAt": "2026-03-01T09:30:00"` and no `coupon` key.

The input side is unchanged: the client sends `created_at`. Sending `createdAt` is ignored as an unknown key, so `created_at` is reported `missing`. If clients should send camelCase too, use `alias=` (and `populate_by_name`) as in p008, or `validation_alias=` for the input only.

Money is kept in **paise** (an int), never in rupees as a float: `0.1 + 0.2` is not `0.3` in floating point (core.02).

## Complexity

O(number of items) for the total, computed each time it is read or dumped.

## Another way

Store the total as a normal field and fill it in a `@model_validator(mode="after")`. Then it is computed once, but it also becomes an **input** field a client could send (and lie about). A computed field cannot be sent; it is always derived from the items.
