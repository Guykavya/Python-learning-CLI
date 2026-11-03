## Approach

The secret comes from outside the program, so the program must refuse to run without it rather
than invent one: a default key in the code would end up in git, and then every pseudonym could
be recomputed by anyone who reads the repository. The check for length guards against test values
like `abc` reaching production, and the error message names the variable but never the value.

`pseudonymise` normalises first (strip, lower-case), because the hash of `" Asha@Example.COM"` and
of `"asha@example.com"` are completely different; without normalising, one customer becomes two.
Then HMAC-SHA256 with the secret key; 16 hex characters (64 bits) are plenty to tell millions of
customers apart.

`pseudonymise_rows` rebuilds each row, swapping the email column for the key column in the same
position, so the email never reaches the output and the input stays untouched.

## Code

```python
import hashlib
import hmac
import os

ENV_VAR = "PAGEBOUND_PSEUDO_KEY"
MIN_LENGTH = 16


def load_secret(env=None):
    if env is None:
        env = os.environ
    value = env.get(ENV_VAR, "").strip()
    if not value:
        raise RuntimeError(f"{ENV_VAR} is not set; export it before running the pipeline")
    if len(value) < MIN_LENGTH:
        raise RuntimeError(f"{ENV_VAR} is too short; use at least {MIN_LENGTH} characters")
    return value.encode("utf-8")


def pseudonymise(value, key):
    if value is None:
        return None
    normalised = value.strip().lower()
    return hmac.new(key, normalised.encode("utf-8"), hashlib.sha256).hexdigest()[:16]


def pseudonymise_rows(rows, key, field="email", out_field="customer_key"):
    out = []
    for row in rows:
        new = {}
        for name, value in row.items():
            if name == field:
                new[out_field] = pseudonymise(value, key)
            else:
                new[name] = value
        if field not in row:
            new[out_field] = None
        out.append(new)
    return out
```

## Complexity

O(length of the value) per pseudonym; O(rows x columns) for the rows.

## Another way

`hmac.new(key, digestmod=hashlib.sha256)` followed by `.update(message)` gives the same digest
and is handy when the message arrives in pieces. Note what pseudonymisation does **not** do: with
the key, anyone can still check "is this table's customer `asha@example.com`?" by computing her
pseudonym. So the pseudonymised table is still personal data under laws like GDPR; it is a
protection, not anonymisation. Keep the key separate from the data (different people, different
storage), and rotate it only together with a plan to recompute every stored pseudonym.
