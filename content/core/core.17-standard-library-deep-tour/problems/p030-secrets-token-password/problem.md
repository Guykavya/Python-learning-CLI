# Tokens and passwords with secrets

`random` is designed to be *repeatable*; `secrets` is designed to be *unpredictable*. It reads
from the operating system's cryptographic random source, so nobody can guess the next value
even after seeing many earlier ones. Anything that guards an account must come from `secrets`.

Write in `solution.py` (do **not** import `random`):

1. `make_token(nbytes=32) -> str`: a URL-safe token made from `nbytes` random bytes
   (`secrets.token_urlsafe`). Fewer than 16 bytes raises `ValueError`.
2. `make_password(length=16) -> str`: a password of exactly `length` characters from
   lowercase, uppercase, digits and the symbols `!@#$%^&*-_`. It must contain **at least one of
   each** of the four kinds, and the positions of those guaranteed characters must be random (not
   "always a lowercase first"). `length < 8` raises `ValueError`.
3. `same_secret(given, expected) -> bool`: compare two secret strings in **constant time** with
   `secrets.compare_digest`. It must work for any text, including non-ASCII.

You cannot test a secret by its value: the tests check **properties** instead (length, the
characters used, every kind present, no repeats in 300 tries, which function compares).

**Example** (your values will be different every time, that is the point)

```python
make_token()        # 'Xq3v0dNw2k8Gm-1e0H7yQ2P6cJ9bLr_tK5sWfA4uZ0o'   43 characters
make_password(10)   # 'p7#Kd2_mQa'
same_secret("abc", "abc")   # True
```
