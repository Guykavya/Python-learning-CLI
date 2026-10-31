## Approach

Encoding: URL-safe Base64, turn the ASCII bytes into a `str`, strip the padding. The padding carries
no information: the length of the token already tells how many bytes the last group holds, so it can
always be put back.

Decoding: strip any padding the caller kept, validate every character against the URL-safe alphabet,
re-pad to a multiple of 4, decode. The validation matters because the decoder is lenient by design:
it drops characters outside the alphabet and, since it first translates `-_` to `+/`, it happily
decodes `+` and `/` too. A token that was changed on the way would then decode to wrong bytes
instead of failing.

## Code

```python
import base64
import string

ALPHABET = set(string.ascii_letters + string.digits + "-_")


def encode_token(data):
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def decode_token(token):
    body = token.rstrip("=")
    for ch in body:
        if ch not in ALPHABET:
            raise ValueError(f"invalid character {ch!r} in token")
    padded = body + "=" * (-len(body) % 4)
    return base64.urlsafe_b64decode(padded)     # binascii.Error is a ValueError


def encode_text(text):
    return encode_token(text.encode("utf-8"))


def decode_text(token):
    return decode_token(token).decode("utf-8")
```

## Complexity

O(n) time and space for n bytes. The text grows by about 4/3.

## Another way

`base64.b64decode(padded, altchars=b"-_", validate=True)` decodes URL-safe Base64 **and** refuses
characters outside the alphabet in one call (it raises `binascii.Error`). Remember that Base64 is an
**encoding**, not encryption: anyone can decode it. Never "hide" a password with it.
