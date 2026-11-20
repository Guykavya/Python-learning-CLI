## Hint 1

Two facts decide the result: does the user exist, and did the password verify. Which **one** call to `verify` gives you the second fact in both cases (known and unknown user)?

## Hint 2

Pick the stored hash first: the user's own, or `DUMMY_HASH` when there is none. Call `verify` once with it. Only afterwards decide: success needs **both** facts. Why must the decision not be "`ok` alone"? (Look at the test where `verify` says `True` for the dummy.)

## Hint 3

```text
stored = users.get(username)
known = stored is not None
ok = verify(password, stored if known else DUMMY_HASH)
if known and ok: return username
raise LoginFailed("invalid username or password")
```
