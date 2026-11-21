## Approach

```python
def encode(n):
    if n < 0:
        raise ValueError("only non-negative numbers can be encoded")
    if n == 0:
        return ALPHABET[0]
    digits = []
    while n:
        n, remainder = divmod(n, 62)
        digits.append(ALPHABET[remainder])
    return "".join(reversed(digits))


class Shortener:
    def create(self, url, alias=None):
        if alias is not None:
            ...validate: shape, reserved word, taken...
            return self._store(alias, url)
        while True:
            code = encode(self.counter).rjust(7, "0")
            self.counter += 1
            if code.lower() not in self.urls:
                return self._store(code, url)
```

The chapter's decision (16.4): a **counter** converted to base62 gives codes with no collisions and no retry loop; each app server asks a central counter for a **block** (1,000 ids) and hands out ids from it with no coordination, so uniqueness is guaranteed and the central counter is touched once per 1,000 creates. Aliases need the extra care of the chapter's "Try it: custom aliases": they share the namespace with generated codes, so the code space must be protected from both collisions (an alias that equals a future generated code, two users choosing the same alias at once). Fixes: a `UNIQUE` constraint on `code` as the **final referee** (the second insert fails and the user is told "taken"), generated codes of a fixed shape, a reserved-word list (`/admin`, `/login`), and the counter that simply **skips** a taken value. The uniqueness check must be the database constraint, not a read-then-insert in Python (swe.07, idempotency and races).

## Complexity

`encode` and `decode` are O(length of the code); `create` and `resolve` are O(1) dictionary operations plus the skip loop.

## Another way

Counter codes are **sequential and guessable**; the chapter scrambles the number with a reversible multiplication modulo 62^7 before encoding (obscurity, not security). For secret links use random 128-bit tokens or require authentication. Random codes of 6 characters collide as the table fills (the birthday paradox: 100,000 codes in 5 characters already collide about 5 times), which is why the chapter prefers the counter.
