## Hint 1

You have a stored string and a target cost. Which three numbers can you read from the string without knowing the password? Which comparison between them and `current` means "weaker"?

## Hint 2

For `verify_and_upgrade` the **order** matters: first check the password. Only if it is right do you ask `needs_rehash`. A failed login must never produce a new hash. For the new hash, which function do you already have, and which parameters do you pass it?

## Hint 3

```text
needs_rehash(stored, current):
    try: scheme, n, r, p, *rest = stored.split("$"); numbers = int(n), int(r), int(p)
    except ValueError: return True            # unreadable
    if scheme != "scrypt": return True
    return any(have < want for have, want in zip(numbers, current))

verify_and_upgrade(pw, stored, current):
    if not verify_password(pw, stored): return False, None
    if needs_rehash(stored, current): return True, hash_password(pw, n=.., r=.., p=..)
    return True, None
```
