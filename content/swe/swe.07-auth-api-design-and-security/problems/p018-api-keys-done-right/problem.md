# API keys done right

Chapter section 6.1 (API keys) and "Try it: why SHA-256 for keys but scrypt for passwords?". An API key identifies a program, not a person. It is a long random string, shown **once** when it is created. The server must be able to check it later without ever keeping the key itself.

Complete `ApiKeys` in `solution.py`:

- `create(owner) -> str`: make `prefix = secrets.token_hex(4)` (8 hex characters, **not secret**, used to find the row) and `secret = secrets.token_urlsafe(32)`. Store, under the prefix, a row with the `owner`, the **SHA-256 hex digest** of the secret and `revoked = False`. Return `"pk_" + prefix + "_" + secret`. This return value is the only time the full key exists.
- `check(presented) -> owner or None`: split the key into `pk`, `prefix`, `secret` (the secret may itself contain `_`, so split into **three parts at most**), find the row by prefix, hash the presented secret and compare the two hashes with `hmac.compare_digest`. Return the owner, or `None` for anything wrong: a malformed key, an unknown prefix, a wrong secret, a revoked key. It must never raise, whatever text it is given.
- `revoke(prefix)`: mark that key as revoked. Other keys of the same owner keep working (that is how a customer rotates a key). An unknown prefix does nothing.

## Example

```python
keys = ApiKeys()
key = keys.create("acme")      # 'pk_3fa91c0b_Zq8...'
keys.check(key)                # 'acme'
keys.check(key + "x")          # None
keys.revoke(key.split("_", 2)[1])
keys.check(key)                # None
```

## Why a fast hash is fine here

A key has 256 random bits, so nobody can guess it, even if they have the hash. A password is chosen by a human and needs a slow hash. A slow hash on every API request would also let attackers overload your server.
