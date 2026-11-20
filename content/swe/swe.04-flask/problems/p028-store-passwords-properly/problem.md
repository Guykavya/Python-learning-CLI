# Store passwords properly

Chapter section 15. A database leak must not reveal passwords. In `solution.py` the starter has `db` and the model `User` with a column `password_hash`. Fill in the methods using **`werkzeug.security`**:

- `set_password(password)`: stores `generate_password_hash(password)` in `password_hash`. A password that is not a string, or is empty, raises **`ValueError`**.
- `check_password(password)`: `True` only when the password matches. Returns `False` (does not raise) for a wrong password, for a user without a stored hash, and for a value that is not a string.
- `to_dict()`: `{"id", "username"}`: the hash must **never** be part of what is sent to clients.

What the tests check about the database itself: the plain password appears **nowhere** in the stored row; two users with the **same** password get **different** hashes (that is the salt); the hash is in Werkzeug's format (`scrypt:...` or `pbkdf2:...`), not a bare `sha256`.

## Example

```python
u = User(username="asha"); u.set_password("correct horse")
u.password_hash          # 'scrypt:32768:8:1$...$...'  (random each time)
u.check_password("correct horse")   # True
u.check_password("wrong")           # False
```
