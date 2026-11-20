# Reset tokens

Chapter section 2.6 (reset tokens). A "forgot password" e-mail carries a link with a **one-time secret**. If an attacker steals your database, the table must not hand out working links, so you store only a **hash** of each token. Write the class that issues and redeems them.

```python
class ResetTokens:
    def __init__(self, clock, ttl: int = 15 * 60): ...
    def issue(self, user: str) -> str: ...
    def consume(self, token: str) -> str | None: ...
```

- `clock()` returns the current time in seconds (a function you are given: the test moves a fake clock, you never call `time`).
- **`issue(user)`** makes a token with `secrets.token_urlsafe(32)` (43 characters) and remembers the user and the expiry time `clock() + ttl`. It stores **only the SHA-256 hex digest** of the token, never the token itself, anywhere on the object.
- A **new token for the same user cancels the old one**: after the second `issue("asha")`, the first token no longer works. Tokens of other users are not touched.
- **`consume(token)`** returns the user name when the token is valid, and `None` for anything else. A token is valid only if:
  - it was issued and is still the user's latest one;
  - it has **not been used before** (single use: after a successful `consume`, the same token returns `None`);
  - it is **not expired**: it works until `ttl - 1` seconds after issue, and at exactly `ttl` seconds it is expired.
- Unknown, empty or random strings return `None` and never raise.

## Example

```text
clock = [1000.0]
tokens = ResetTokens(lambda: clock[0])
t = tokens.issue("asha")            # 43 random characters
tokens.consume(t)                   -> "asha"
tokens.consume(t)                   -> None          (used)
t2 = tokens.issue("asha"); clock[0] += 899
tokens.consume(t2)                  -> "asha"        (899 s later, still valid)
t3 = tokens.issue("asha"); clock[0] += 900
tokens.consume(t3)                  -> None          (expired at exactly 900 s)
```

The tests import `ResetTokens`. They look inside `vars(tokens)` to check that the token itself is not kept.
