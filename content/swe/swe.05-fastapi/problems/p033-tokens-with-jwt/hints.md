## Hint 1

`make_token` is one `jwt.encode` call (section 12.2). For `read_token`, list what can go wrong and who notices it: PyJWT notices a bad signature, a wrong algorithm, garbage, and missing claims (with `require`). Who must notice expiry, now that PyJWT's clock check is off?

## Hint 2

Wrap the `jwt.decode(...)` call in `try ... except jwt.PyJWTError as exc: raise InvalidToken(str(exc)) from exc`. After it, compare `now >= payload["exp"]` yourself. Finally `int(payload["sub"])`, which can raise `ValueError` for a non-number: turn that into `InvalidToken` too.

## Hint 3

```text
make_token(user_id, now, minutes=15):
    return jwt.encode({"sub": str(user_id), "exp": now + minutes * 60}, SECRET, algorithm="HS256")

read_token(token, now):
    try: payload = jwt.decode(token, SECRET, algorithms=["HS256"],
                              options={"verify_exp": False, "require": ["sub", "exp"]})
    except jwt.PyJWTError as exc: raise InvalidToken(...) from exc
    if now >= payload["exp"]: raise InvalidToken("expired")
    try: return int(payload["sub"])
    except ValueError: raise InvalidToken("bad subject")
```
