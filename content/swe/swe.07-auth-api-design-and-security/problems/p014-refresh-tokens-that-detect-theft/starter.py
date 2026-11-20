import hashlib
import secrets


class InvalidToken(Exception):
    """The refresh token is unknown, expired or already revoked."""


class TokenReuse(Exception):
    """A token that was already used came back: somebody has a copy."""


class RefreshStore:
    def __init__(self, now, ttl=7 * 86400):
        self.now = now          # a function that returns the current time in seconds
        self.ttl = ttl
        self.rows = {}

    def issue(self, user, family=None):
        """Create a refresh token for `user` and return it (the text the client keeps)."""
        raise NotImplementedError("write issue()")

    def rotate(self, token):
        """Trade `token` for a new one. Return (user, new_token)."""
        raise NotImplementedError("write rotate()")
