## Hint 1

What does the database need to hold so that it can **recognise** a token when the user comes back, but cannot **be used** as a token by a thief? Think of how a password is stored.

## Hint 2

You need two small dictionaries: `sha256(token) -> (user, expires)` to recognise tokens, and `user -> sha256(newest token)` so a new `issue` can delete the old row. In `consume`, `dict.pop` finds the row **and** removes it in one step: that is the single-use rule, and it also removes expired rows. Compare the clock **after** popping.

## Hint 3

```text
issue(user):
    token = secrets.token_urlsafe(32); key = sha256hex(token)
    if user has an old key: delete that row
    rows[key] = (user, clock() + ttl); latest[user] = key
    return token

consume(token):
    key = sha256hex(token); row = rows.pop(key, None)
    if row is None: return None
    forget latest[user] if it is this key
    if clock() >= expires: return None
    return user
```
