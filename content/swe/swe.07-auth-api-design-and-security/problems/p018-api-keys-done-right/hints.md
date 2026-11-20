## Hint 1

What exactly must the stored row contain so that a stolen copy of the table cannot be used to call the API? Which part of the key is a lookup label, and which part is the secret?

## Hint 2

`token_urlsafe` can produce `_` and `-`. What goes wrong if you call `key.split("_")` and expect three parts? What argument of `split` limits the number of splits? Also think about what must happen when `presented` has no underscores at all.

## Hint 3

```text
create: prefix = token_hex(4); secret = token_urlsafe(32)
        rows[prefix] = {owner, sha256(secret).hexdigest(), revoked False}
        return "pk_" + prefix + "_" + secret
check:  parts = presented.split("_", 2); if not 3 parts or parts[0] != "pk": None
        row = rows.get(prefix); if none: None
        digest = sha256(secret); if not compare_digest(row.hash, digest) or row.revoked: None
        return row.owner
revoke: set revoked on rows[prefix] if present
```
