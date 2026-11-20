## Hint 1

Think about what a row must remember so that `rotate` can answer three questions: whose token is it, is it still alive, and was it used already? Then ask: what must `issue` do differently for a brand-new login and for a rotation (hint: the `family` argument)?

## Hint 2

Why is the stored key `sha256(token)` and not the token? Because `self.rows` may leak (a database dump). Look the token up by hashing what the client sent.

## Hint 3

```text
_key(token) = sha256(token).hexdigest()
issue(user, family):
    token = secrets.token_urlsafe(32)
    rows[_key(token)] = {user, family or new random family, used False, expires now()+ttl}
rotate(token):
    row = rows.get(_key(token))
    if no row or row.expires < now(): raise InvalidToken
    if row.used:
        remove all rows with the same family
        raise TokenReuse
    row.used = True
    return row.user, issue(row.user, row.family)
```
