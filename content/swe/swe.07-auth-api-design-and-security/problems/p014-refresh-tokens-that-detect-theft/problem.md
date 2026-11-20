# Refresh tokens that detect theft

Chapter section 4.4 (access tokens and refresh tokens). An access token is short-lived (minutes). The client keeps a long-lived **refresh token** and trades it for a new access token when the old one expires. If someone steals the refresh token, they can do the same. The defence is **rotation**: every refresh token works **once**, and each use hands back a **new** one.

If a token that was already used comes back, two parties hold copies: the real user and a thief. You cannot tell which is which, so you revoke the whole **family** (all tokens that descend from one login) and force a fresh login.

Complete the class `RefreshStore` in `solution.py`.

- `RefreshStore(now, ttl=7 * 86400)`: `now` is a function that returns the current time in seconds (the tests move it; never call `time.time()` yourself).
- `issue(user, family=None) -> str`: make a new random token with `secrets.token_urlsafe(32)` and remember it. A login starts a new family (`secrets.token_hex(8)`); rotation passes the existing family on. The token expires at `now() + ttl`.
- `rotate(token) -> (user, new_token)`:
  - unknown, or expired (`expires < now()`): raise `InvalidToken`;
  - already used: delete **every** row of that family and raise `TokenReuse`;
  - otherwise mark it used and return the user and a new token of the same family.
- **Store only a hash.** The keys of `self.rows` are `hashlib.sha256(token.encode()).hexdigest()`. A stolen database must not hand out working tokens. Each row is a dict with at least `user`, `family`, `used`, `expires`.

The two exception classes are already in the starter.

## Example

```python
store = RefreshStore(now=lambda: 0)
t1 = store.issue("asha")            # at login
user, t2 = store.rotate(t1)         # ("asha", "<new token>")
store.rotate(t1)                    # raises TokenReuse: t1 was used already
store.rotate(t2)                    # raises InvalidToken: the whole family is gone
```

## Notes

- A token is still valid at exactly `now == expires`; it is refused one second later.
- A second login of the same user is a different family and is not affected.
