## Hint 1

`base64.urlsafe_b64encode` takes bytes and returns bytes. How do you turn the result into a `str`,
and how do you remove only the trailing `=` signs? For decoding: how many `=` signs make a length a
multiple of 4?

## Hint 2

The number of `=` to add is `-len(body) % 4` (0, 1, 2 or 3). Before decoding, loop over the
characters and raise `ValueError` for any that is not in a set built from `string.ascii_letters`,
`string.digits` and `"-_"`. The `binascii.Error` raised for an impossible length is already a
subclass of `ValueError`.

## Hint 3

```
encode_token(data) = urlsafe_b64encode(data).decode("ascii").rstrip("=")

decode_token(token):
    body = token.rstrip("=")
    for ch in body: if ch not in ALPHABET: raise ValueError
    return urlsafe_b64decode(body + "=" * (-len(body) % 4))

encode_text(t) = encode_token(t.encode("utf-8"))
decode_text(tok) = decode_token(tok).decode("utf-8")
```
