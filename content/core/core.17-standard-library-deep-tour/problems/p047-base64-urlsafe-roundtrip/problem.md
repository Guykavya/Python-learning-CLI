# URL-safe Base64 tokens without padding

Base64 turns **any bytes** into text made of 64 safe characters, so binary data can travel in JSON,
e-mails or URLs. Every 3 bytes become 4 characters; when the data length is not a multiple of 3, `=`
signs pad the result to a multiple of 4.

Standard Base64 uses `+` and `/`, which mean something in a URL (`+` is a space in a query string,
`/` separates path parts). **URL-safe** Base64 uses `-` and `_` instead. Many web tokens (for
example the parts of a JWT) also drop the `=` padding.

```python
>>> base64.b64encode(b"\xfb\xff\xbf")
b'+/+/'
>>> base64.urlsafe_b64encode(b"\xfb\xff\xbf")
b'-_-_'
>>> base64.urlsafe_b64encode(b"hi")
b'aGk='
```

Note that these functions take **bytes** and return **bytes**.

Write four functions in `solution.py`:

1. `encode_token(data: bytes) -> str`: URL-safe Base64 of `data`, as a `str`, with the trailing `=`
   removed.
2. `decode_token(token: str) -> bytes`: the reverse. Accept the token with or without its `=` padding
   (put the missing padding back yourself: the length must become a multiple of 4).
   Raise `ValueError` if the token (after removing trailing `=`) contains any character other than
   `A-Z a-z 0-9 - _`, or if it cannot be decoded.
   Careful: `urlsafe_b64decode` **silently ignores** many bad characters (and accepts `+` and `/`), so
   check the characters yourself first.
3. `encode_text(text: str) -> str`: `encode_token` of the UTF-8 bytes of `text`.
4. `decode_text(token: str) -> str`: the reverse of `encode_text`.

**Example**

```python
encode_token(b"\xfb\xff\xbf")     # '-_-_'
encode_token(b"hi")               # 'aGk'        ('aGk=' without padding)
decode_token("aGk")               # b'hi'
decode_token("aGk=")              # b'hi'        padding is accepted too
encode_text("café")               # 'Y2Fmw6k'
decode_text("Y2Fmw6k")            # 'café'
decode_token("aG+k")              # ValueError   '+' is not URL-safe
```
