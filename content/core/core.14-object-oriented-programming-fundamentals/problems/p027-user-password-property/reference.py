import hashlib


def _hash(text):
    """Return a hex fingerprint of text. Given: do not change it."""
    return hashlib.sha256(("salt:" + text).encode("utf-8")).hexdigest()


MAX_WRONG = 3


class User:
    def __init__(self, username, password):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("username must be a non-empty string")
        self.username = username.strip()
        self._wrong = 0
        self._locked = False
        self.password = password          # runs the setter below

    @property
    def password(self):
        raise AttributeError("password is write-only")

    @password.setter
    def password(self, text):
        if not isinstance(text, str) or len(text) < 8:
            raise ValueError("password must be a string of at least 8 characters")
        if not any(ch.isdigit() for ch in text):
            raise ValueError("password needs at least one digit")
        if not any(ch.isalpha() for ch in text):
            raise ValueError("password needs at least one letter")
        self._password_hash = _hash(text)

    def check_password(self, attempt):
        if self._locked:
            return False
        if _hash(attempt) == self._password_hash:
            self._wrong = 0
            return True
        self._wrong += 1
        if self._wrong >= MAX_WRONG:
            self._locked = True
        return False

    @property
    def is_locked(self):
        return self._locked

    def unlock(self):
        self._locked = False
        self._wrong = 0

    def change_password(self, old, new):
        if not self.check_password(old):
            raise PermissionError("wrong password")
        self.password = new
