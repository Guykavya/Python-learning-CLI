## Hint 1

Why can `Field(...)` not say "end after start"? A field constraint sees **one** value. Where can you see `self.start` and `self.end` together (section 5.6)?

## Hint 2

In `mode="after"` the validator is an ordinary method that receives `self`, a fully built model with real `date` objects. Dates compare with `<=`. Look up the limit with `MAX_GUESTS[self.room]`. Raise `ValueError` for a broken rule and `return self` at the end.

## Hint 3

```text
@model_validator(mode="after")
def check_booking(self):
    if self.end <= self.start: raise ValueError("end must be after start")
    if self.guests > MAX_GUESTS[self.room]: raise ValueError("too many guests for this room")
    return self
```
