## Hint 1

Section 5.5: a validator is a class method decorated with `@field_validator("field")` (above `@classmethod`). It receives the value, may **raise `ValueError`**, and must **return** the value to keep. What happens if it returns nothing?

## Hint 2

For the email, clean first (`strip().lower()`), then check: `v.partition("@")` gives `(local, "@", domain)`; the address is bad if `local` or `domain` is empty or `domain` still contains `@`. For `interests`, the default "after" mode runs **after** Pydantic checked the type, and a `str` is not a `list[str]`, so it would already have failed. That is why it needs `mode="before"`.

## Hint 3

```text
@field_validator("name") classmethod clean_name(v):
    v = v.strip(); if not v: raise ValueError(...); return v.title()

@field_validator("email") classmethod check_email(v):
    v = v.strip().lower(); local, at, domain = v.partition("@")
    if not local or not domain or "@" in domain: raise ValueError(...)
    if domain in DISPOSABLE: raise ValueError(...)
    return v

@field_validator("interests", mode="before") classmethod split_interests(v):
    if isinstance(v, str): return [p.strip() for p in v.split(",") if p.strip()]
    return v
```
