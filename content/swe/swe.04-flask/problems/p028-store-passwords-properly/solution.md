## Approach

```python
from werkzeug.security import check_password_hash, generate_password_hash


class User(db.Model):
    ...

    def set_password(self, password):
        if not isinstance(password, str) or not password:
            raise ValueError("password must be a non-empty string")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash or not isinstance(password, str):
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username}
```

Example: `generate_password_hash("correct horse")` returns something like `scrypt:32768:8:1$<salt>$<hash>`: the method and its cost settings, a **random salt**, and the result of a **deliberately slow** function. `check_password_hash` reads the method and salt from the string, repeats the computation on the candidate and compares in constant time.

Why each property matters: the **salt** makes equal passwords look different (an attacker cannot see who shares a password, and precomputed tables are useless); the **slowness** (scrypt or PBKDF2) makes guessing millions of passwords per second impossible; storing **only the hash** means the server cannot reveal the password even to its owner.

## Complexity

One hash per call: tens of milliseconds by design. That is why login routes need rate limiting (section 16.8).

## Another way

`argon2-cffi` (Argon2id) or `bcrypt` are other good choices. Never use `hashlib.sha256(password)`: it is fast, so a leaked table is cracked in hours.

## Not covered

Upgrading old hashes when the algorithm changes (rehash at the next successful login).
