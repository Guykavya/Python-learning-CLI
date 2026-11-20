## Hint 1

Write `sign` first, in four short steps, and look at the result: a token should have exactly two dots. For `verify`, which piece of the token must you trust **least**: the header, the payload or the signature? In which order will you look at them?

## Hint 2

`verify` is `sign` run backwards: take the first two parts as text, recompute the signature **with your key**, and compare it with the third part. Compare the **text** of the signatures (both encoded with `b64u`) using `hmac.compare_digest`, not decoded bytes: base64 text can differ while the decoded bytes are equal, and an attacker may use that.

Only after the signature matches, decode the header and check `alg == "HS256"`, and then decode the payload and check it is a `dict`. One `try` around the splitting and decoding can catch `ValueError` (unpacking the wrong number of parts, bad base64, bad JSON and non-ASCII text are all `ValueError`s).

## Hint 3

```text
sign(payload, key):
    signing_input = b64u(json(header)) + "." + b64u(json(payload))
    return signing_input + "." + b64u(hmac_sha256(key, signing_input))

verify(token, key):
    try: head, body, sig = token.split(".")             # wrong count -> ValueError
         expected = b64u(hmac_sha256(key, head + "." + body))
         if not compare_digest(expected.encode("ascii"), sig.encode("ascii")): raise InvalidToken
         header = json.loads(b64u_decode(head)); payload = json.loads(b64u_decode(body))
    except (ValueError, ...): raise InvalidToken
    if header.get("alg") != "HS256": raise InvalidToken
    if payload is not a dict: raise InvalidToken
    return payload
```
