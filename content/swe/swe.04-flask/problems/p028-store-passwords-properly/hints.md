## Hint 1

If an attacker reads your database, what should they find in the password column? Should you be able to get the original password back from it?

## Hint 2

Werkzeug has a pair: `generate_password_hash(password)` (adds a random salt, uses a slow algorithm) and `check_password_hash(hash, password)`. Guard the edges: wrong types, empty values, a user without a hash.

## Hint 3

```text
set_password: if not a non-empty str -> ValueError; self.password_hash = generate_password_hash(password)
check_password: if no hash or not a str -> False; return check_password_hash(self.password_hash, password)
to_dict: id and username only
```
