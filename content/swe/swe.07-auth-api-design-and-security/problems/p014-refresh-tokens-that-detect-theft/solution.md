## Approach

```python
import hashlib
import secrets


class InvalidToken(Exception):
    pass


class TokenReuse(Exception):
    pass


class RefreshStore:
    def __init__(self, now, ttl=7 * 86400):
        self.now = now
        self.ttl = ttl
        self.rows = {}          # sha256(token) -> record; the token itself is never stored

    @staticmethod
    def _key(token):
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def issue(self, user, family=None):
        token = secrets.token_urlsafe(32)
        self.rows[self._key(token)] = {
            "user": user,
            "family": family or secrets.token_hex(8),
            "used": False,
            "expires": self.now() + self.ttl,
        }
        return token

    def rotate(self, token):
        row = self.rows.get(self._key(token))
        if row is None or row["expires"] < self.now():
            raise InvalidToken("invalid refresh token")
        if row["used"]:
            family = row["family"]
            self.rows = {k: v for k, v in self.rows.items() if v["family"] != family}
            raise TokenReuse("refresh token reused: the whole session is revoked")
        row["used"] = True
        return row["user"], self.issue(row["user"], row["family"])
```

Why it works: a token is single-use because the row is flagged `used` the first time. The flag is what makes a replay visible: the unknown token case gives `InvalidToken`, but a **known, used** token proves that someone is holding a copy. Dropping the whole family logs out both the thief and the honest user, which is the price of safety (chapter 4.4).

## Complexity

`issue` and `rotate` are O(1) dictionary operations. The revoke step scans all rows once, O(n). A database would use an index on the family column.

## Another way

Keep a separate dict `family -> set of live token hashes` so that revoking a family does not scan every row. Or store a `family_revoked` flag and check it in `rotate`; then no row is ever deleted and the audit trail (who reused what, when) survives.
