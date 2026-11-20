## Approach

```python
def make_token(user_id: int, now: int, minutes: int = 15) -> str:
    claims = {"sub": str(user_id), "exp": now + minutes * 60}
    return jwt.encode(claims, SECRET, algorithm=ALGORITHM)


def read_token(token: str, now: int) -> int:
    try:
        payload = jwt.decode(
            token, SECRET, algorithms=[ALGORITHM],
            options={"verify_exp": False, "require": ["sub", "exp"]},   # we check exp with OUR clock
        )
    except jwt.PyJWTError as exc:
        raise InvalidToken(str(exc)) from exc
    if not isinstance(payload["exp"], int) or now >= payload["exp"]:
        raise InvalidToken("Token expired")
    try:
        return int(payload["sub"])
    except ValueError as exc:
        raise InvalidToken("Bad subject") from exc
```

How each attack is stopped:

| Attack | Who refuses it | PyJWT error (inside) |
|---|---|---|
| another key | the signature check | `InvalidSignatureError` |
| `alg: none` | `algorithms=["HS256"]` does not list `none` | `InvalidAlgorithmError` |
| changed payload | the signature no longer matches | `InvalidSignatureError` |
| changed signature | same | `InvalidSignatureError` |
| `"abc"` | cannot be split and decoded | `DecodeError` |
| no `exp` / no `sub` | `require` | `MissingRequiredClaimError` |
| expired | our `now >= exp` | (ours) |

Converting all of them into **one** exception of our own means the code that uses `read_token` (the `get_current_user` dependency in p034) has a single `except InvalidToken:` and answers 401, without knowing PyJWT's class names. `raise ... from exc` keeps the original error attached for the log.

Why the clock is injected: tests with a fixed `NOW` give the same answer forever and can check the exact boundary (`NOW + 899` valid, `NOW + 900` expired) without sleeping.

## Complexity

O(length of the token): one HMAC-SHA256 over the header and payload.

## Another way

Let PyJWT check expiry against the real clock (`jwt.decode(..., algorithms=["HS256"])` with default options) and test expiry by **making** tokens with times relative to the real now (`now = int(time.time())`, `exp = now - 10`), as section 12.2 does. It needs no option, but the tests then depend on the machine's clock, and the exact boundary cannot be tested.
