import hashlib
import secrets


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class ResetTokens:
    def __init__(self, clock, ttl: int = 15 * 60):
        self.clock = clock
        self.ttl = ttl
        self.rows = {}              # sha256(token) -> (user, expires_at)
        self.latest = {}            # user -> sha256 of that user's newest token

    def issue(self, user: str) -> str:
        token = secrets.token_urlsafe(32)
        key = _digest(token)
        old = self.latest.get(user)
        if old is not None:
            self.rows.pop(old, None)                        # a new token cancels the old one
        self.rows[key] = (user, self.clock() + self.ttl)
        self.latest[user] = key
        return token

    def consume(self, token: str):
        if not isinstance(token, str):
            return None
        key = _digest(token)
        row = self.rows.pop(key, None)                      # pop: single use, even when expired
        if row is None:
            return None
        user, expires_at = row
        if self.latest.get(user) == key:
            del self.latest[user]
        if self.clock() >= expires_at:
            return None
        return user
