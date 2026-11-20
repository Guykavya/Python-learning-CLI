# Claims that must be checked

Chapter section 4.2 (claims that must be checked) and the table of registered claims. A token signed with **your** key is not necessarily meant for **this** service, and it may be expired, not yet valid, or from another issuer. After the signature is verified (p011), you still have to check the claims. Write the function that does it, with the time given as an argument.

```python
class InvalidClaim(Exception):
    def __init__(self, reason): ...      # self.reason is a short code; str(exc) is the same code

def check_claims(claims: dict, now: float, issuer: str, audience: str, leeway: float = 30) -> dict: ...
```

`claims` is the payload `dict` of a token whose signature is already good. Check the rules **in this order** and raise `InvalidClaim(reason)` for the **first** one that fails. If all pass, return `claims`.

| Order | Rule | `reason` |
|---|---|---|
| 1 | `sub` is present and is a non-empty `str` | `"missing_sub"` |
| 2 | `exp` is present and is a number (`int` or `float`, **not** `bool`) | `"missing_exp"` |
| 3 | not expired: the token is **expired** when `now - leeway >= exp` | `"expired"` |
| 4 | `nbf` (not before) is **optional**; if present it must be a number, else `"bad_nbf"`; the token is **not yet valid** when `nbf > now + leeway` | `"not_yet_valid"` |
| 5 | `iss` is present and equals `issuer` exactly | `"wrong_issuer"` |
| 6 | `aud` is present, and either **equals** `audience` (a string) or is a **list that contains** `audience` | `"wrong_audience"` |

`leeway` (seconds) forgives small differences between the clocks of two servers. The rule `now - leeway >= exp` is the same one PyJWT uses.

## Example

```text
good = {"sub": "42", "iss": "pagebound-auth", "aud": "payments", "exp": 1000}
check_claims(good, now=900, issuer="pagebound-auth", audience="payments")     -> good
check_claims(good, now=1029, ...)    -> good           (29 s late, inside the 30 s leeway)
check_claims(good, now=1030, ...)    -> raises InvalidClaim("expired")
check_claims({**good, "aud": "reports"}, now=900, ...)               -> raises InvalidClaim("wrong_audience")
check_claims({**good, "aud": ["reports", "payments"]}, now=900, ...) -> good
check_claims({**good, "aud": "payments-admin"}, now=900, ...)        -> raises InvalidClaim("wrong_audience")
```

The tests import `check_claims` and `InvalidClaim`.
