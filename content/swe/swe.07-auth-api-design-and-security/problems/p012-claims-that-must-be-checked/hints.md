## Hint 1

List the six rules and, for each, the **one** thing that can go wrong: a missing key, a value of the wrong type, or a wrong value. Which of the six also need a type check *before* you compare numbers or strings?

## Hint 2

Two traps. (1) `bool` is a subclass of `int` in Python, so `True` passes `isinstance(x, int)`: write a small `_is_number` helper that excludes it. (2) `"payments" in "payments-admin"` is `True`, because `in` on strings means "substring". For a string `aud` compare with `==`; for a list use `in` (which then compares whole elements).

For time, write the two rules exactly as the table says: expired when `now - leeway >= exp`; not yet valid when `nbf > now + leeway`.

## Hint 3

```text
sub = claims.get("sub"); if not str or empty -> missing_sub
exp = claims.get("exp"); if not number -> missing_exp; if now - leeway >= exp -> expired
if "nbf" in claims: not number -> bad_nbf; nbf > now + leeway -> not_yet_valid
if claims.get("iss") != issuer -> wrong_issuer
aud = claims.get("aud"):  str -> aud == audience | list -> audience in aud | other -> False
return claims
```
