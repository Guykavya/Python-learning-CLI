import hashlib
import secrets


class ResetTokens:
    def __init__(self, clock, ttl: int = 15 * 60):
        self.clock = clock
        self.ttl = ttl
        # TODO: whatever you need to remember (only HASHES of tokens)

    def issue(self, user: str) -> str:
        # TODO: secrets.token_urlsafe(32); store sha256(token), user and expiry; cancel the user's older token
        return ""

    def consume(self, token: str):
        # TODO: user name, or None (unknown, used, replaced or expired)
        return None
