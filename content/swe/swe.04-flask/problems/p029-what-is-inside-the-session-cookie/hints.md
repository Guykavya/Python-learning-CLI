## Hint 1

Split the cookie at the dots. Decode the first part with Base64 (add `=` padding if Python complains). What do you see? Does it look secret?

## Hint 2

A **signature** answers "was this changed?", not "can anyone read it?". Think of a letter in a see-through envelope with a wax seal. Who can read it? Who can change it without breaking the seal? Who can make a *new* sealed letter?

## Hint 3

```text
1. payload (JSON, readable) . timestamp . signature (HMAC with SECRET_KEY)
2. can read + copy; cannot change without the key
3. key leak/weak key -> forge any session
4. user id only: payload is readable, can become stale, the DB is the truth
5. session.clear(): the attacker may know the old session; start fresh at login
```
