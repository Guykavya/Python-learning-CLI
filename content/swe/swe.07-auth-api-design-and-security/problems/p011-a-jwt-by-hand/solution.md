## Approach

```python
def _json_part(data):
    return b64u(json.dumps(data, separators=(",", ":")).encode("utf-8"))


def _signature(signing_input, key):
    return b64u(hmac.new(key, signing_input.encode("ascii"), hashlib.sha256).digest())


def sign(payload, key):
    signing_input = _json_part({"alg": "HS256", "typ": "JWT"}) + "." + _json_part(payload)
    return signing_input + "." + _signature(signing_input, key)


def verify(token, key):
    try:
        head, body, sig = token.split(".")
        expected = _signature(head + "." + body, key)
        if not hmac.compare_digest(expected.encode("ascii"), sig.encode("ascii")):
            raise InvalidToken("bad signature")
        header = json.loads(b64u_decode(head))
        payload = json.loads(b64u_decode(body))
    except InvalidToken:
        raise
    except (ValueError, TypeError, AttributeError) as exc:
        raise InvalidToken("malformed token") from exc
    if not isinstance(header, dict) or header.get("alg") != "HS256":
        raise InvalidToken("algorithm not allowed")
    if not isinstance(payload, dict):
        raise InvalidToken("payload is not an object")
    return payload
```

What to notice (chapter 4.1 and 4.3):

- **The signature protects integrity, not secrecy.** Anyone can read the payload (`b64u_decode`); nobody can change it without the key. Never put private data in a token.
- **Signature first.** The header and payload are attacker-controlled until the signature matches, so we do not even parse them before that.
- **The server pins the algorithm.** The `alg` check is a constant in your code, not a decision made by the token. This is the fix for the `alg: none` attack and for algorithm confusion. It runs *after* the signature check, so a forged header cannot be reached at all; a token with a correct HS256 signature and another `alg` is still refused.
- **Compare the encoded text.** The last character of a 43-character base64 signature carries two unused bits. Two different texts can decode to the same 32 bytes. If you compare decoded bytes, a forged token that differs only in that last character is accepted: the token is "malleable". Comparing the exact text closes it.
- **`hmac.compare_digest`** compares in constant time.
- **One exception type** (`InvalidToken`) for every kind of problem, so the caller has a single `except` and no information leaks through different messages to the client.

## Complexity

`O(length of the token)`: one HMAC, two base64 decodes and two JSON parses.

## Another way

Use PyJWT: `jwt.encode(payload, key, algorithm="HS256")` and `jwt.decode(token, key, algorithms=["HS256"])`. It does all of this and more, and the first test file checks that your token and PyJWT's are interchangeable. Writing it once by hand is how you learn what `algorithms=[...]` protects you from.
