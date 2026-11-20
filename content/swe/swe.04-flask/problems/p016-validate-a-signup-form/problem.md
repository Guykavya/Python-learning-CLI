# Validate a signup form

Chapter section 9.1. Validation on the server is **a plain function**: data in, errors out, no Flask needed, so it is easy to test. Write `validate_signup(form)` in `solution.py`. `form` is a dict-like object (a plain dict in the tests, `request.form` in a real app) with the keys `username`, `email`, `password`, `confirm`; any key may be missing (treat it as `""`).

Return a pair `(clean, errors)`:

- `clean` is a dict with the **stripped** `username` and `email` (never the passwords).
- `errors` is a dict `{field: message}` with **one message per bad field** and no key for good fields:

| Field | Valid when | Error key |
|---|---|---|
| `username` | matches `[a-z0-9_]{3,20}` (whole string, lower-case only) | `username` |
| `email` | has the shape `something@something.something` (no spaces, exactly one `@`) | `email` |
| `password` | at least **10** characters (spaces count; do **not** strip it) | `password` |
| `confirm` | equal to `password` | `confirm` |

The `password` and `confirm` checks are independent: a short password that is typed twice the same has only a `password` error.

## Example

```python
validate_signup({"username": " asha_k ", "email": "asha@example.com", "password": "long enough pw", "confirm": "long enough pw"})
# ({"username": "asha_k", "email": "asha@example.com"}, {})

validate_signup({"username": "A", "email": "nope", "password": "short", "confirm": "different"})
# errors has the four keys: username, email, password, confirm
```
