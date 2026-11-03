# Mask emails and keep only allowed columns

The support team wants a daily export of orders so they can answer "where is my order?" calls.
They need to recognise a customer's address roughly ("is this the a-something at example.com
account?"), but they must not get the full email, and they must not get columns they do not need.

Two rules from the chapter:

- **Mask** what people need to recognise, but not to read: `asha@example.com` becomes
  `a***@example.com`.
- Use an **allow-list**, not a deny-list. "Keep `id`, `status`, `city`" stays safe when the API
  starts sending a new `phone` column tomorrow. "Drop `email`" does not: the phone numbers would go
  straight into the export. This is called *deny by default*.

## Your task

In `solution.py` write three functions.

```python
def mask_email(email: str | None) -> str | None:
```

- `None` stays `None`.
- Strip surrounding spaces and lower-case the address, then split it at the **last** `@`.
- If there is no `@`, or the part before or after it is empty, return `"***"` (a malformed value
  could be anything, so hide all of it).
- Otherwise return the first character of the local part, then exactly `***`, then `@` and the
  domain. Always three stars, whatever the length, so the mask does not reveal the name's length.

```python
def select_columns(row: dict, allowed: list[str]) -> dict:
```

Return a **new** dict with only the keys in `allowed`, in the order of `allowed`. Allowed names
that the row does not have are skipped.

```python
def prepare_export(rows: list[dict], allowed: list[str]) -> list[dict]:
```

For each row, keep only the allowed columns; if `email` is among them, mask it. Return a new
list of new dicts and never change the input rows.

## Example

```python
mask_email("asha@example.com")        # 'a***@example.com'
mask_email("  Meera@Example.COM ")    # 'm***@example.com'
mask_email("not-an-email")            # '***'
mask_email(None)                      # None

rows = [{"id": 1, "email": "asha@example.com", "phone": "+91 98xxxxxx01", "city": "Pune"}]
prepare_export(rows, ["id", "email", "city"])
# [{'id': 1, 'email': 'a***@example.com', 'city': 'Pune'}]      phone is not allowed, so it is gone
```
