## Approach

One validator per field. "After" validators get a value that already has the right type; the "before" validator sees the raw JSON value and reshapes it.

```python
class SignupIn(BaseModel):
    name: str
    email: str
    interests: list[str] = []

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be empty")
        return v.title()

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        v = v.strip().lower()
        local, at, domain = v.partition("@")
        if not local or not domain or "@" in domain:
            raise ValueError("not a valid email address")
        if domain in DISPOSABLE:
            raise ValueError("disposable email addresses are not allowed")
        return v

    @field_validator("interests", mode="before")
    @classmethod
    def split_interests(cls, v):
        if isinstance(v, str):
            return [part.strip() for part in v.split(",") if part.strip()]
        return v
```

Example: `" X@MAILINATOR.COM "` becomes `"x@mailinator.com"`, `partition` gives the domain `"mailinator.com"`, which is in `DISPOSABLE`: `ValueError`, shown as a 422 entry at `["body", "email"]` with type `value_error` and the message `Value error, disposable email addresses are not allowed`.

`"python, sql,,"` is split into `["python", " sql", "", ""]`; stripping and dropping empties gives `["python", "sql"]`, and only **then** does Pydantic check `list[str]`. For `5` the validator returns `5` unchanged and Pydantic reports `list_type` as usual.

## Complexity

O(length of the input strings).

## Another way

Pydantic has `EmailStr` (it needs the extra package `email-validator`, which is not installed in this course), and `Annotated[str, AfterValidator(func)]` lets you attach a validator function to a reusable type, so `CleanName = Annotated[str, AfterValidator(clean_name)]` can be used in many models.
