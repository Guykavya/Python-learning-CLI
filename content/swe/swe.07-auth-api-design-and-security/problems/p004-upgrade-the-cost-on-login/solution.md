## Approach

```python
def needs_rehash(stored: str, current=CURRENT) -> bool:
    try:
        scheme, n, r, p, *_ = stored.split("$")
        if scheme != "scrypt":
            return True
        stored_cost = (int(n), int(r), int(p))
    except ValueError:
        return True
    return any(have < want for have, want in zip(stored_cost, current))


def verify_and_upgrade(password: str, stored: str, current=CURRENT):
    if not verify_password(password, stored):
        return False, None
    if needs_rehash(stored, current):
        n, r, p = current
        return True, hash_password(password, n=n, r=r, p=p)
    return True, None
```

The idea (chapter 2.2): the plain password exists in memory only at login, so that is the only moment a stronger hash can be made. The caller (the login endpoint) saves `new_stored` when it is not `None`.

Three decisions worth noticing:

1. **Verify first.** If the password is wrong you have learned nothing, and creating a hash would store a wrong password.
2. **"Lower than", not "different".** The chapter's first version used `!=`. With `!=`, moving back to a cheaper setting would downgrade every strong hash at the next login. `any(have < want ...)` only upgrades.
3. **Unreadable means `True`** for `needs_rehash`, but `verify_password` is already `False` for those, so `verify_and_upgrade` returns `(False, None)` before it gets there.

Accounts of people who never log in keep the old hash (the "Try it" answer): you cannot re-hash without the password.

## Complexity

One verification costs one scrypt run; an upgrade costs a second one. `needs_rehash` is `O(length of the string)` and never runs scrypt.

## Another way

Wrap the old hash instead of waiting: in a one-off migration compute `scrypt_new(old_hash_string)` for every row and mark the row "wrapped". At login verify by applying the old hash and then the new one, and replace the row by a plain new hash. It upgrades dormant accounts too, at the price of a more complex verify.
