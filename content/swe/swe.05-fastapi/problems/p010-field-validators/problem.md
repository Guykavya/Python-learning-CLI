# Field validators

Chapter section 5.5 (field validators, `mode="before"`). Some rules cannot be written as `Field` constraints. Write them as validators that **clean** good input and **refuse** bad input.

In `solution.py` keep the given list

```python
DISPOSABLE = {"mailinator.com", "tempmail.dev", "10minutemail.com"}
```

and define `app = FastAPI()` and a model `SignupIn` with three fields:

1. `name: str`: strip spaces at both ends and **title-case** it (`"  asha rao "` → `"Asha Rao"`). If nothing is left after stripping, raise `ValueError("name must not be empty")`.
2. `email: str`: strip and **lower-case** it. It must contain exactly one `@` with text on both sides, otherwise `ValueError("not a valid email address")`. If the part after `@` is in `DISPOSABLE`, raise `ValueError("disposable email addresses are not allowed")`. Check the domain **after** lower-casing, so `X@MAILINATOR.COM` is refused too.
3. `interests: list[str] = []`: clients may send a JSON list **or** one comma-separated string. Write a `mode="before"` validator: if the raw value is a `str`, split it on commas, strip each piece and drop empty pieces (`"python, sql,,"` → `["python", "sql"]`); any other value is returned unchanged for Pydantic to check.

`POST /signups` takes a `SignupIn` body and returns `data.model_dump()` with status **201**.

A `ValueError` raised in a validator becomes a 422 entry with `type` `value_error` at the field's `loc`, for example `["body", "email"]`.

## Example

```text
POST /signups {"name": "  asha rao ", "email": " Asha@Example.COM ", "interests": "python, sql,,"}
-> 201 {"name": "Asha Rao", "email": "asha@example.com", "interests": ["python", "sql"]}

POST /signups {"name": "Ravi", "email": "ravi@Mailinator.com"}
-> 422 ["body", "email"] value_error
```
