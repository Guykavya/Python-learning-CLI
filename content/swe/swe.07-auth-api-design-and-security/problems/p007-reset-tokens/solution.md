## Approach

```python
def _digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class ResetTokens:
    def __init__(self, clock, ttl=15 * 60):
        self.clock, self.ttl = clock, ttl
        self.rows = {}              # sha256(token) -> (user, expires_at)
        self.latest = {}            # user -> sha256 of that user's newest token

    def issue(self, user):
        token = secrets.token_urlsafe(32)
        key = _digest(token)
        old = self.latest.get(user)
        if old is not None:
            self.rows.pop(old, None)
        self.rows[key] = (user, self.clock() + self.ttl)
        self.latest[user] = key
        return token

    def consume(self, token):
        if not isinstance(token, str):
            return None
        key = _digest(token)
        row = self.rows.pop(key, None)
        if row is None:
            return None
        user, expires_at = row
        if self.latest.get(user) == key:
            del self.latest[user]
        if self.clock() >= expires_at:
            return None
        return user
```

Why each rule exists (chapter 2.6):

- **`secrets.token_urlsafe(32)`:** 256 random bits. Nobody can guess one, and `random` would be predictable.
- **Store only the SHA-256:** a stolen table does not give working reset links. A **fast** hash is correct here (unlike for passwords) because the token already has 256 bits of randomness: there is nothing to brute-force.
- **Short life** limits the time a leaked e-mail is dangerous. **Single use** (`pop`) means a link found later in someone's mail archive is dead.
- **A new token cancels the old one**, so "I clicked forgot password three times" never leaves three live links.
- **Injected clock:** the test moves time instantly and checks the exact second.

When the password is really changed, also delete every other session and token of that user (chapter 3.4).

## Complexity

`issue` and `consume` are `O(1)` on average (one SHA-256 and one dictionary operation). Memory grows with unused tokens; a real system deletes expired rows with a periodic job.

## Another way

Keep a single dictionary `user -> (hash, expires)` and look up by user name: the link then carries the user id and the token (`/reset?user=7&token=...`). It needs no second dictionary, but you must compare the stored hash with `hmac.compare_digest`, and the link reveals user ids. Looking up by the token's hash, as here, needs no comparison at all.
