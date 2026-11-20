## Hint 1

Section 5.10 shows a computed field: which two decorators go on top of the method, and in which order? Why is a plain `@property` not enough when you call `model_dump()`?

## Hint 2

An `alias=` changes the input **and** output name; a `serialization_alias=` changes only the output name. `model_dump` uses output names only with `by_alias=True`; FastAPI responses use them by default. The three switches of `to_api` are `mode="json"`, `by_alias=True`, `exclude_none=True`.

## Hint 3

```text
created_at: datetime = Field(serialization_alias="createdAt")

@computed_field
@property
def total_paise(self) -> int:
    return sum(line.price_paise * line.qty for line in self.items)

to_api: return order.model_dump(mode="json", by_alias=True, exclude_none=True)
@app.post("/orders/preview", response_model_exclude_none=True)
def preview(order: Order) -> Order: return order
```
