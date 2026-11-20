import hashlib
import secrets


class InvalidToken(Exception):
    """The refresh token is unknown, expired or already revoked."""


class TokenReuse(Exception):
    """A token that was already used came back: somebody has a copy."""


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
