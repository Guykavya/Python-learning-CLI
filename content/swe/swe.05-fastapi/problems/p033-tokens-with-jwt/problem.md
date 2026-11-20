# Tokens with JWT

Chapter section 12.2 (tokens with JWT: `sub` as a string, always `exp`, always `algorithms=[...]`). The injected clock is the idea of section 9.6.

Write the two token functions an API needs, with **PyJWT** (`import jwt`), the key `SECRET` and the algorithm `"HS256"` (both in the starter), and your own exception class `InvalidToken`.

**`make_token(user_id, now, minutes=15) -> str`**

- claims: `"sub"`: the user id **as a string** (`"42"`), and `"exp"`: `now + minutes * 60`;
- `now` is a Unix time in seconds (an `int`) given by the caller, not read from the clock;
- sign with `jwt.encode(claims, SECRET, algorithm="HS256")`.

**`read_token(token, now) -> int`**

- returns the user id as an `int` when the token is good;
- raises **`InvalidToken`** (never a PyJWT exception, never anything else) when the token is:
  - **expired**: `now >= exp`;
  - signed with **another key**;
  - an **`alg: none`** token (no signature at all);
  - **tampered**: the payload or the signature was changed;
  - not a token at all (`"abc"`), or missing `sub` or `exp`.

One complication: PyJWT checks `exp` against the **real** clock. A test that uses a fixed `now` (say, a day in 2023) would see every token as expired. So switch PyJWT's own expiry check off and do it with `now` yourself:

```python
payload = jwt.decode(token, SECRET, algorithms=["HS256"],
                     options={"verify_exp": False, "require": ["sub", "exp"]})
```

`require` makes PyJWT reject a token without `sub` or `exp`. `algorithms=["HS256"]` is what stops an `alg: none` token. Every PyJWT error is a subclass of `jwt.PyJWTError`.

## Example

```text
NOW = 1_700_000_000
t = make_token(42, NOW)
jwt.decode(t, options={"verify_signature": False})  -> {"sub": "42", "exp": 1700000900}
read_token(t, NOW)        -> 42
read_token(t, NOW + 899)  -> 42
read_token(t, NOW + 900)  -> raises InvalidToken        (expired)
read_token(jwt.encode({"sub": "42", "exp": NOW + 900}, "another-key-" + "x" * 40, algorithm="HS256"), NOW)
                          -> raises InvalidToken        (wrong key)
```

The tests import `make_token`, `read_token`, `InvalidToken` and `SECRET`.
