# A password module

Chapter section 2.2 (a password module) and 2.1 (the attacker's view). Write the two functions every login system needs: one that turns a password into a **string you can store**, and one that checks a password against that string. Use only the standard library: `hashlib.scrypt`, `hmac`, `base64`, `os`.

## What to write

```python
N, R, P = 2**14, 8, 1        # the default cost (given in the starter)

def hash_password(password: str, *, n: int = N, r: int = R, p: int = P) -> str: ...
def verify_password(password: str, stored: str) -> bool: ...
```

**`hash_password`**

- makes a fresh random **16-byte salt** (`os.urandom(16)`) on every call;
- derives the digest with `hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p, maxmem=256 * n * r)` (scrypt needs about `128 * n * r` bytes; without `maxmem` Python refuses large `n`);
- returns one **self-describing string** of six parts joined by `$`:
  `scrypt$<n>$<r>$<p>$<salt in base64>$<digest in base64>` (standard `base64.b64encode`, decoded to `str`).

**`verify_password`**

- reads the cost parameters **from the stored string** (never from the constants), so a hash made with another cost still verifies;
- returns `True` only if the password is right;
- returns `False`, and **never raises**, for any string that is not a valid stored hash: wrong scheme name, wrong number of parts, numbers that are not numbers, bad base64, an empty string;
- compares the two digests with **`hmac.compare_digest`**, not `==` (an `==` stops at the first different byte, and the time it takes can leak how many bytes were right).

## Example

```text
h = hash_password("correct horse battery", n=2**10)
h.split("$")[:4]                    -> ['scrypt', '1024', '8', '1']
len(base64.b64decode(h.split("$")[4]))   -> 16      (the salt)
verify_password("correct horse battery", h)  -> True
verify_password("wrong", h)                  -> False
verify_password("x", "garbage")              -> False   (no exception)
hash_password("same") != hash_password("same")   # two salts, two different strings
```

The tests pass small costs (`n=2**10`) so they run fast. A real site uses the default.

The tests import `hash_password`, `verify_password` and `N` from `solution`. Call `hmac.compare_digest` as written (module `hmac`, not `from hmac import ...`): one test replaces it with a spy to see that you use it.
