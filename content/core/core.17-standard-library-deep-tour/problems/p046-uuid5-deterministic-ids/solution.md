## Approach

`uuid5` hashes the namespace's 16 bytes plus the name with SHA-1 and stamps the version bits, so it
is a pure function of its inputs: perfect for ids that must be recomputable. Normalising the email
first is what makes "the same person" give "the same id". `uuid4` uses 122 random bits from the
operating system: two calls practically never collide.

To recognise the canonical form, let `uuid.UUID` do the hard parsing and then compare its canonical
output (`str(parsed)`, always lowercase with hyphens) with the input in lower case. Any other
spelling, or extra characters, changes the string and fails the comparison.

## Code

```python
import uuid


def _normalise(email):
    return email.strip().lower()


def user_id(email):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "mailto:" + _normalise(email)))


def new_session_id():
    return str(uuid.uuid4())


def is_canonical_uuid(text):
    try:
        parsed = uuid.UUID(text)
    except (ValueError, TypeError, AttributeError):
        return False
    return str(parsed) == text.lower()


def assign_ids(emails):
    return {_normalise(email): user_id(email) for email in emails}
```

## Complexity

All functions are O(1) per id (plus O(n) for `assign_ids` over n emails).

## Another way

You can create your **own** namespace once, for example
`APP_NS = uuid.uuid5(uuid.NAMESPACE_DNS, "learn.example.com")`, and use `uuid5(APP_NS, email)`.
Then ids from your app never match ids another app computes from the same email. For
`is_canonical_uuid`, a hand check also works: length 36, hyphens at positions 8, 13, 18, 23, and all
other characters in `"0123456789abcdef"` after lower-casing.
