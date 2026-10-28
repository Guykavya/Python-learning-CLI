## Approach

**Write-only property.** A property lets an attribute run code when you read or write it (chapter
section 8). Here reading should be impossible, so the getter only raises
`AttributeError("password is write-only")`. The setter does the real work: it checks the text and
stores **only the hash** under a different, private name, `_password_hash`. It must not write to
`self.password`, because that would call the setter again, forever.

**One place for the rules.** `__init__` sets `self.password = password`. That line goes through the
property, so new users and changed passwords pass the very same checks.

**Read-only property.** `is_locked` has only a getter. A property without a setter raises
`AttributeError` on assignment by itself. The real state lives in `self._locked`, which only the
class's own methods change.

**State for locking.** Two private attributes: `_wrong` (wrong attempts in a row) and `_locked`.
`check_password` updates them. The underscore says "do not touch from outside" (section 7).

## Code

```python
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
```

Notice the order in `__init__`: `_wrong` and `_locked` are set before the password. Here it does not
matter, but if the setter ever used them, they would already exist.

## Complexity

Every method is O(k) for a password of length k (hashing and the digit/letter checks).

## Another way

Instead of a write-only property you could have a method `set_password(text)` and no `password`
attribute at all. That is also common. The property version lets `__init__` and callers use
normal attribute syntax while still running the checks. Real systems use a slow hash made for
passwords (for example `hashlib.scrypt`) and a random salt per user.

Remember that the underscore is only a convention: `u._password_hash` is still readable. Python
encapsulation is about clear signals, not locks.
