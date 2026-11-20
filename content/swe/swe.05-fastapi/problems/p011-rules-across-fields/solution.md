## Approach

Single-field rules stay on the fields (`ge=1`, `Literal`). The two rules that need several fields go into one "after" model validator.

```python
class Booking(BaseModel):
    start: date
    end: date
    guests: int = Field(ge=1)
    room: Literal["single", "double"]

    @model_validator(mode="after")
    def check_booking(self):
        if self.end <= self.start:
            raise ValueError("end must be after start")
        if self.guests > MAX_GUESTS[self.room]:
            raise ValueError("too many guests for this room")
        return self
```

Example: `start=2026-03-01, end=2026-03-01` passes every field check (both are valid dates), so the model validator runs; `end <= start` is true, the `ValueError` becomes one 422 entry at `["body"]` with type `value_error`.

With `guests=0` the field check `ge=1` fails, the model is never built, and the model validator never runs: one error at `["body", "guests"]`. That is also why the validator can safely use `MAX_GUESTS[self.room]`: `room` is guaranteed to be `"single"` or `"double"` when it runs.

## Complexity

O(1) per booking.

## Another way

Report **both** cross-field problems at once: collect messages in a list and raise one `ValueError("; ".join(problems))` at the end. The client then fixes everything in one round trip, in the spirit of section 5.1. (Checking "is the room free on those dates?" is not validation at all: it needs the database and belongs in the endpoint, answering 409; see section 6.3.)
