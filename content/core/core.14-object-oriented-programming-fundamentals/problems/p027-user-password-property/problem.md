# A user with a write-only password

A website must never keep a user's password as plain text. It keeps only a **hash** (a scrambled
fingerprint of the password) and compares hashes at login. Write the class `User` in `solution.py`.
The starter already contains the helper `_hash(text)`; use it and do not change it.

**`User(username, password)`**

- `username` must be a non-empty string after `strip()`, otherwise `ValueError`. Store the
  stripped name in the attribute `username`.
- `password` is a **write-only property**:
  - Reading `user.password` raises `AttributeError` with the message `password is write-only`.
  - Setting `user.password = text` checks the new password and stores **only**
    `_hash(text)` in the attribute `_password_hash`. A valid password is a `str` with at least
    8 characters, at least one digit and at least one letter. Otherwise raise `ValueError`
    and keep the old password.
  - `__init__` must set the password through the property (`self.password = password`), so the
    same checks run.
- `check_password(attempt)` returns `True` if `_hash(attempt)` equals the stored hash, else `False`.
- **Locking:** after **3 wrong attempts in a row**, the user is locked. A locked user's
  `check_password` always returns `False`, even for the right password. A right attempt before
  that resets the count of wrong attempts to 0.
- `is_locked` is a **read-only property** (`True`/`False`). Setting it raises `AttributeError`
  (a property without a setter does that by itself).
- `unlock()` clears the lock and the count.
- `change_password(old, new)`: if `check_password(old)` is `False`, raise `PermissionError`.
  Otherwise set the new password (through the property, so it is checked).

The plain password must not be stored anywhere in the object.

**Example**

```python
u = User(" asha ", "mango2024")
u.username                  # 'asha'
u.check_password("mango2024")   # True
u.password                  # AttributeError: password is write-only
u.password = "short1"       # ValueError (fewer than 8 characters)
u.password = "kiwi-kiwi-7"  # fine
u.check_password("mango2024")   # False  (1 wrong)
u.check_password("nope")        # False  (2 wrong)
u.check_password("nope")        # False  (3 wrong: now locked)
u.is_locked                 # True
u.check_password("kiwi-kiwi-7") # False  (locked)
u.unlock()
u.check_password("kiwi-kiwi-7") # True
```
