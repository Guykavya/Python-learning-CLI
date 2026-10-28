## Hint 1

Which function always gives the same UUID for the same input, and which one is random? What are the
two arguments of `uuid.uuid5`? The tests compare against a fixed string, so the namespace and the name
must be exactly `uuid.NAMESPACE_URL` and `"mailto:" + normalised_email`.

## Hint 2

For `is_canonical_uuid`: `uuid.UUID(text)` raises `ValueError` for garbage and accepts several
spellings. After parsing, `str(parsed)` is always the canonical lowercase form. When is the text
canonical, compared with that string?

## Hint 3

```
normalise(email) = email.strip().lower()
user_id(email)   = str(uuid.uuid5(uuid.NAMESPACE_URL, "mailto:" + normalise(email)))

is_canonical_uuid(text):
    try: parsed = uuid.UUID(text)
    except ValueError: return False
    return str(parsed) == text.lower()

assign_ids(emails) = {normalise(e): user_id(e) for e in emails}
```
