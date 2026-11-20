## Approach

```python
import hashlib
import hmac
import secrets


class ApiKeys:
    def __init__(self):
        self.rows = {}          # prefix -> {"owner", "hash", "revoked"}

    def create(self, owner: str) -> str:
        prefix = secrets.token_hex(4)
        while prefix in self.rows:
            prefix = secrets.token_hex(4)
        secret = secrets.token_urlsafe(32)
        self.rows[prefix] = {
            "owner": owner,
            "hash": hashlib.sha256(secret.encode("utf-8")).hexdigest(),
            "revoked": False,
        }
        return f"pk_{prefix}_{secret}"

    def check(self, presented: str):
        if not isinstance(presented, str):
            return None
        parts = presented.split("_", 2)
        if len(parts) != 3 or parts[0] != "pk":
            return None
        _, prefix, secret = parts
        row = self.rows.get(prefix)
        digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()
        stored = row["hash"] if row else "0" * 64          # one comparison, found or not
        same = hmac.compare_digest(stored, digest)
        if row is None or row["revoked"] or not same:
            return None
        return row["owner"]

    def revoke(self, prefix: str) -> None:
        if prefix in self.rows:
            self.rows[prefix]["revoked"] = True
```

Points to see: the prefix is the cheap, non-secret index; the secret is hashed before comparing, so `compare_digest` only ever receives two ASCII hex strings (comparing `str` objects with non-ASCII text would raise `TypeError`, which hashing first avoids). Splitting with `maxsplit=2` keeps a secret like `ab_cd` intact. The `while` loop makes prefix collisions impossible even though they are rare.

## Complexity

`create` and `check` are O(1): one dictionary lookup and one SHA-256.

## Another way

Store a `last_used` time and a `scopes` set on each row (chapter 6.1) and make `check(key, needed_scope)` return the owner only when the scope is present. Or use a database table with the prefix as the primary key; the code stays the same.
