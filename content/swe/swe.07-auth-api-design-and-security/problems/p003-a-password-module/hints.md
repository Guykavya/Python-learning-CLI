## Hint 1

What does the stored string have to contain so that, a year from now, `verify_password` can redo the exact same calculation? List the inputs of `scrypt` (password, salt, `n`, `r`, `p`) and ask for each: is it secret, random, or just a number?

## Hint 2

The salt is random, so it is **not** in your code: where must it be after hashing? Put every number and the salt into the string. In `verify_password`, split the string on `$`, turn the text parts back into numbers and bytes (`int(...)`, `base64.b64decode(...)`), run scrypt again with those, and compare.

Many things can go wrong while parsing (wrong count of parts, `int("x")`, bad base64). Which exception types do they raise? Wrap the parsing in one `try` and return `False`.

## Hint 3

```text
hash_password(pw, n, r, p):
    salt = os.urandom(16)
    digest = scrypt(pw.encode(), salt, n, r, p, maxmem=256*n*r)
    return "$".join(["scrypt", n, r, p, b64(salt), b64(digest)])

verify_password(pw, stored):
    try:
        scheme, n, r, p, salt_b64, digest_b64 = stored.split("$")   # wrong count -> ValueError
        if scheme != "scrypt": return False
        expected = b64decode(digest_b64)
        actual = scrypt(pw.encode(), b64decode(salt_b64), int(n), int(r), int(p), maxmem=...)
    except (ValueError, TypeError): return False
    return hmac.compare_digest(actual, expected)
```
