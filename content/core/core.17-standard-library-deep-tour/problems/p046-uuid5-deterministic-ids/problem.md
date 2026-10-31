# UUIDs: random (`uuid4`) and repeatable (`uuid5`)

A UUID is a 128-bit identifier written as 36 characters: `8-4-4-4-12` hex digits with hyphens.
The `uuid` module makes two useful kinds:

- `uuid.uuid4()`: **random**. Every call gives a new id. Good for session ids, upload names, anything
  that must never collide with an earlier one.
- `uuid.uuid5(namespace, name)`: **computed** from a namespace UUID and a name with SHA-1. The same
  namespace and name always give the same UUID, on every computer, forever. Good for "the id of this
  email address", so two programs that never talk to each other agree on it.

The 13th hex digit tells the version (`...-5cfa-...` is a version 5 UUID, `...-4465-...` version 4).

Write four functions in `solution.py`:

1. `user_id(email) -> str`: the version-5 UUID (as a string) of the name `"mailto:" + email`, in the
   namespace `uuid.NAMESPACE_URL`. **Normalise** the email first: strip spaces and lower-case it, so
   `" Kavya@Example.com"` and `"kavya@example.com"` get the same id.
2. `new_session_id() -> str`: a fresh random version-4 UUID as a string.
3. `is_canonical_uuid(text) -> bool`: `True` only for the standard 36-character form with hyphens
   (upper or lower case). `uuid.UUID()` also accepts `{...}` braces, `urn:uuid:...` and 32 hex digits
   without hyphens: those are **not** canonical here and give `False`. Anything that is not a UUID at
   all gives `False` (never an exception).
4. `assign_ids(emails) -> dict[str, str]`: maps each **normalised** email to its `user_id`.
   Case variants of one email give one entry.

**Example**

```python
user_id("kavya@example.com")
# 'e20557fa-85ab-5cfa-bef7-ceca88d23d54'      the same on every run and every computer
user_id("  KAVYA@example.com ")
# 'e20557fa-85ab-5cfa-bef7-ceca88d23d54'

new_session_id()
# '2979047a-d47f-4465-b991-84b57be6d840'      random: different on every call

is_canonical_uuid("E20557FA-85AB-5CFA-BEF7-CECA88D23D54")   # True
is_canonical_uuid("e20557fa85ab5cfabef7ceca88d23d54")       # False (no hyphens)
is_canonical_uuid("hello")                                  # False

assign_ids(["Asha@example.com", "asha@example.com"])
# {'asha@example.com': '526a2c55-21d3-55ba-8da3-fc2ff6f60c99'}
```
