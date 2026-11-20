# Upgrade the cost on login

Chapter section 2.2 and its "Try it: the cost upgrade". Computers get faster, so the cost of your password hash must go up over the years. You cannot re-hash a stored hash (you do not know the password), but at a **successful login** the plain password is in memory for a moment. That is the time to replace an old hash with a stronger one.

The starter gives you `hash_password` and `verify_password` from problem p003 (finished, do not change them) and a tuple `CURRENT = (N, R, P)` with the cost you want today. You write two functions:

```python
def needs_rehash(stored: str, current=CURRENT) -> bool: ...
def verify_and_upgrade(password: str, stored: str, current=CURRENT) -> tuple[bool, str | None]: ...
```

**`needs_rehash(stored, current)`** is `True` when the stored hash should be replaced:

- the scheme is not `scrypt`, or the string cannot be read (wrong number of parts, `n`, `r` or `p` not integers): `True` (it is useless as it is);
- or **any** of its `n`, `r`, `p` is **lower** than the same number in `current`;
- otherwise `False`. A hash that is already **stronger** than `current` is left alone (never downgrade).

**`verify_and_upgrade(password, stored, current)`** returns a pair `(ok, new_stored)`:

- wrong password (or an unreadable `stored`): `(False, None)`. Never upgrade after a failed login;
- right password and the hash is up to date: `(True, None)`;
- right password and `needs_rehash` is true: `(True, new_stored)`, where `new_stored` is a fresh hash of the same password made with the parameters in `current`. The caller saves it.

## Example

```text
CURRENT = (2**10, 8, 1)
legacy = hash_password("old-password", n=2**8)          # made years ago
needs_rehash(legacy, CURRENT)                           -> True
verify_and_upgrade("nope", legacy, CURRENT)             -> (False, None)
ok, new = verify_and_upgrade("old-password", legacy, CURRENT)
ok                                                      -> True
new.split("$")[1:4]                                     -> ['1024', '8', '1']
verify_and_upgrade("old-password", new, CURRENT)        -> (True, None)     # nothing left to do
```

The tests pass a small `current`, so they stay fast. The tests import `needs_rehash`, `verify_and_upgrade`, `hash_password`, `verify_password` and `CURRENT`.
