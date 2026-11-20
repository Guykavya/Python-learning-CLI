# Rules across fields

Chapter section 5.6 (model validators), with 5.3 (`Field`) and 5.9 (`Literal`). A hotel booking has rules that involve **two fields at once**, so no single-field constraint can express them.

In `solution.py` define `app = FastAPI()`, the table

```python
MAX_GUESTS = {"single": 2, "double": 4}
```

and a model `Booking`:

| Field | Type and rule |
|---|---|
| `start` | `date` |
| `end` | `date` |
| `guests` | `int`, at least 1 (`Field(ge=1)`) |
| `room` | `Literal["single", "double"]` |

plus **one** `@model_validator(mode="after")` that checks, in this order:

1. `end` must be **after** `start` (at least one night): otherwise `ValueError("end must be after start")`.
2. `guests` must not exceed `MAX_GUESTS[room]`: otherwise `ValueError("too many guests for this room")`.

and returns `self`.

`POST /bookings` takes a `Booking` body and returns, with status **201**:

```python
{"room": b.room, "guests": b.guests, "nights": (b.end - b.start).days}
```

A model validator's error belongs to the **whole body**, so its 422 entry has `loc` `["body"]` and `type` `value_error`. Field errors keep their own `loc` (`["body", "guests"]`).

Note: an "after" model validator runs only when **every field is already valid**. If `guests` is 0, the field error is the only error; your cross-field rules do not run (they could not: a field might be missing).

## Example

```text
POST /bookings {"start": "2026-03-01", "end": "2026-03-04", "guests": 4, "room": "double"}
-> 201 {"room": "double", "guests": 4, "nights": 3}

POST /bookings {"start": "2026-03-01", "end": "2026-03-01", "guests": 1, "room": "single"}
-> 422 ["body"] value_error         (zero nights)

POST /bookings {"start": "2026-03-01", "end": "2026-03-02", "guests": 3, "room": "single"}
-> 422 ["body"] value_error         (a single room takes 2)
```
