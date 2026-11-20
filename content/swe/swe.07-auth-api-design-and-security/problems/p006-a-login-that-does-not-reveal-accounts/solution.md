## Approach

```python
def login(users, username, password, verify):
    stored = users.get(username)
    known = stored is not None
    ok = verify(password, stored if known else DUMMY_HASH)     # always exactly one verification
    if known and ok:
        return username
    raise LoginFailed("invalid username or password")          # one message for every failure
```

The function does the same work and gives the same answer in both failure cases:

- **Same message:** an attacker who tries a list of e-mail addresses learns nothing from the text. (User enumeration is the first step of targeted phishing and credential stuffing, chapter 2.5.)
- **Same work:** the slow hash runs for an unknown user too, against a dummy hash made once at start-up with the same cost as real hashes. A stopwatch cannot tell the two cases apart.
- **`known and ok`:** the dummy hash exists only to burn time. It must never let anyone in.

The test counts calls instead of measuring time: it is exact, and it runs in microseconds. Measuring real time in a test is flaky.

Remember the neighbours of this idea: the "forgot password" form must also answer "if that address exists, we sent an e-mail", and logins need a rate limit (section 11).

## Complexity

One call of `verify` (one slow hash) per attempt; the dictionary lookup is `O(1)`.

## Another way

Make unknown and known users equal by **always** having a hash: when someone registers, store the row; for lookups of names that do not exist, return a hash derived from the name with a server secret (`HMAC(secret, username)` used as the salt) so the dummy differs per name and cannot be spotted. The call count stays the same.
