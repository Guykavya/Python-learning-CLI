import hashlib


def _hash(text):
    """Return a hex fingerprint of text. Given: do not change it."""
    return hashlib.sha256(("salt:" + text).encode("utf-8")).hexdigest()


class User:
    def __init__(self, username, password):
        # TODO: check and store the username; set the password through the property
        self.username = username

    # TODO: a write-only `password` property (getter raises AttributeError, setter checks and hashes)

    def check_password(self, attempt):
        return False

    # TODO: a read-only `is_locked` property

    def unlock(self):
        pass

    def change_password(self, old, new):
        pass
