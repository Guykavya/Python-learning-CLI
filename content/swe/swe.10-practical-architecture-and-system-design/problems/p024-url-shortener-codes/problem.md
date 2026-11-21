# URL shortener codes

Chapter section 16 (worked design 1: a URL shortener), especially 16.4 (where do codes come from?) and "Try it: custom aliases". The one hard decision of a shortener is how codes are made. A **counter converted to base62** gives codes with no collisions at all (no uniqueness check, no retry loop). Users may also choose their own **alias** (`/spring-sale`); aliases live in the **same namespace** as generated codes, so two things can collide: an alias with a generated code, and two users choosing the same alias.

## What to write

```python
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"     # given

def encode(n: int) -> str: ...
def decode(code: str) -> int: ...

class InvalidAlias(ValueError): ...           # given
class AliasTaken(ValueError): ...             # given

class Shortener:
    def __init__(self, reserved=("api", "admin", "login", "static", "health")): ...
    def create(self, url, alias=None) -> str: ...
    def resolve(self, code) -> str | None: ...
```

- `encode(n)`: base62 of a non-negative integer, most significant digit first (`0` -> `"0"`, `61` -> `"z"`, `62` -> `"10"`); a negative number raises `ValueError`. `decode(code)` is the inverse; an empty string or a character outside the alphabet raises `ValueError`.
- **Generated codes** come from a counter starting at 1: the code for counter value `n` is `encode(n).rjust(7, "0")` (always 7 characters, padded with `"0"`). The same long URL may get different codes (two users shortening the same page get two codes).
- **Aliases**: `create(url, alias="spring-sale")` uses the alias as the code. An alias must be **3 to 32 characters** of letters, digits, `-` and `_`; anything else raises `InvalidAlias`. Aliases are compared **without regard to case** for reserved words and for being taken (`Admin` and `admin` are the same), but the code is stored as the user typed it, and `resolve` also ignores case. A **reserved** word (the constructor's list) raises `InvalidAlias`. An alias that is already used (as an alias **or as a generated code**) raises `AliasTaken`.
- **Collisions between aliases and generated codes**: when the counter's next code is already taken (for example somebody chose the alias `0000002`), **skip it** and use the next counter value. The counter never goes back, and a skipped value is never used again.
- `create` returns the code. `resolve(code)` returns the long URL, or `None` for an unknown code.
- A failed `create` (invalid or taken alias) must **not** consume a counter value.

## Example

```python
s = Shortener()
s.create("https://example.com/a")                   # '0000001'
s.create("https://example.com/b", alias="spring-sale")   # 'spring-sale'
s.create("https://example.com/c", alias="0000002")  # '0000002'   (a legal alias that looks like a generated code)
s.create("https://example.com/d")                   # '0000003'   (the counter skipped 2: it was taken)
s.resolve("SPRING-SALE")                            # 'https://example.com/b'
```

(In production the uniqueness of the alias is decided by a `UNIQUE` constraint in the database, as the chapter says, not by a read-then-insert in Python; this problem models the rules.)
