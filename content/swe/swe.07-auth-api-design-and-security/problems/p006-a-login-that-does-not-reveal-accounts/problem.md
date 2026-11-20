# A login that does not reveal accounts

Chapter section 2.5 (the login endpoint: do not leak who has an account). Two small differences let an attacker find out which usernames exist:

- the **message**: "no such user" versus "wrong password";
- the **time**: an unknown user is rejected instantly, a known user costs one slow hash.

Fix both. Write `login`, which receives the user table and the password checker as arguments (so a test can watch it):

```python
class LoginFailed(Exception): ...

def login(users: dict[str, str], username: str, password: str, verify) -> str: ...
```

- `users` maps a username to its **stored hash string**.
- `verify(password, stored) -> bool` is the checker (in the real app it is `verify_password` from p003). Your function must **call it exactly once per attempt**, whoever tries.
- The starter defines `DUMMY_HASH`, a stored hash for a user that does not exist. For an **unknown** username call `verify(password, DUMMY_HASH)` anyway, so an unknown user costs the same time as a known one.
- Success: return the `username`.
- Any failure (unknown user, or wrong password): raise `LoginFailed("invalid username or password")`. The **same class and the same message** for both.
- An unknown user must **never** log in, even if `verify` happens to say `True` for the dummy hash. Decide from two facts: the user exists **and** the password verified.

## Example

```text
users = {"asha": "hash-of-asha-pass"}
login(users, "asha", "asha-pass", verify)     -> "asha"                  (verify called once)
login(users, "asha", "wrong", verify)         -> raises LoginFailed("invalid username or password")
login(users, "nobody", "anything", verify)    -> raises LoginFailed("invalid username or password")
                                                 (verify was still called once, with DUMMY_HASH)
```

The tests import `login`, `LoginFailed` and `DUMMY_HASH`.
