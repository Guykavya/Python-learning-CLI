## Approach

```python
def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_claims(claims, now, issuer, audience, leeway=30):
    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub:
        raise InvalidClaim("missing_sub")

    exp = claims.get("exp")
    if not _is_number(exp):
        raise InvalidClaim("missing_exp")
    if now - leeway >= exp:
        raise InvalidClaim("expired")

    if "nbf" in claims:
        nbf = claims["nbf"]
        if not _is_number(nbf):
            raise InvalidClaim("bad_nbf")
        if nbf > now + leeway:
            raise InvalidClaim("not_yet_valid")

    if claims.get("iss") != issuer:
        raise InvalidClaim("wrong_issuer")

    aud = claims.get("aud")
    if isinstance(aud, str):
        allowed = aud == audience
    elif isinstance(aud, list):
        allowed = audience in aud
    else:
        allowed = False
    if not allowed:
        raise InvalidClaim("wrong_audience")
    return claims
```

Why each check exists (chapter 4.2):

- **`sub`** says who the token is about. A token with no subject proves nothing.
- **`exp` is required.** A token without expiry is valid for ever once stolen. With PyJWT the same thing is `options={"require": ["exp", "sub", "iss", "aud"]}`.
- **`iss`** says who made the token, **`aud`** says who it is for. A token for the "reports" service signed with the same key must not open the "payments" service: that is the audience check.
- **`nbf`** is optional; it is for tokens that start in the future.
- **Leeway** forgives small clock differences between servers. Keep it small (seconds, not minutes).
- **`now` is a parameter.** The test can check `now = exp + leeway - 1` and `exp + leeway` exactly, without sleeping and without depending on the real clock.
- **Types first.** Claims come from outside; a number may arrive as a string, `aud` as an integer. A wrong type must give `InvalidClaim`, never `TypeError`.

Naming the failed rule in `reason` makes logs and tests clear. Be careful what you tell the *client*: log the reason, but show the caller one generic "invalid token" message (chapter 15.7).

## Complexity

`O(1)` for strings and numbers, `O(length of aud)` when `aud` is a list.

## Another way

Let PyJWT do it: `jwt.decode(token, key, algorithms=["HS256"], audience="payments", issuer="pagebound-auth", options={"require": ["exp", "sub", "iss", "aud"]}, leeway=30)`. It raises `ExpiredSignatureError`, `InvalidAudienceError`, `InvalidIssuerError`, `ImmatureSignatureError` or `MissingRequiredClaimError`. It reads the **real** clock, which is why the earlier problems with a fixed `now` check claims themselves, as here.
