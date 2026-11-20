# A JWT by hand

Chapter section 4.1 (a JWT built by hand) and 4.3 (attacks: `alg: none`). A JWT is three base64url pieces joined by dots, `header.payload.signature`, and the HS256 signature is an HMAC-SHA256 of the first two pieces. Nothing is encrypted. Building and checking one yourself removes the mystery. Use only `base64`, `hashlib`, `hmac` and `json`.

```python
class InvalidToken(Exception): ...

def sign(payload: dict, key: bytes) -> str: ...
def verify(token: str, key: bytes) -> dict: ...
```

**Encoding.** `b64u` is base64url **without** the `=` padding (the starter gives `b64u` and `b64u_decode`).

**`sign(payload, key)`**

1. header = `{"alg": "HS256", "typ": "JWT"}`;
2. `signing_input = b64u(header_json) + "." + b64u(payload_json)`, where each JSON is `json.dumps(..., separators=(",", ":"))` encoded as UTF-8;
3. `signature = HMAC-SHA256(key, signing_input)`;
4. return `signing_input + "." + b64u(signature)`.

**`verify(token, key)`** returns the payload as a `dict` or raises `InvalidToken` (and **nothing else**, whatever the input) when:

- the token does not have exactly **three** parts separated by dots (`"abc"`, `"a.b"`, `""`);
- the **signature** does not match: a changed payload, a changed header, a wrong key, a changed signature;
- the header's `alg` is not exactly `"HS256"` (the **server** decides the algorithm, never the token: `"none"` and `"HS512"` are refused);
- a part is not valid base64url, or the header or the payload is not valid JSON, or the payload is not a JSON object.

Compare signatures with `hmac.compare_digest`, and compare the **encoded text** of the signature (recompute the expected signature, encode it with `b64u`, compare the two strings). There is a trap in comparing decoded bytes; a test shows it.

`verify` does **not** check `exp` or any other claim: that is the next problem.

## Example

```text
KEY = b"a-long-random-demo-key-of-at-least-32-bytes!"
token = sign({"sub": "42", "role": "member", "exp": 2000000000}, KEY)
token.count(".")                     -> 2
verify(token, KEY)                   -> {'sub': '42', 'role': 'member', 'exp': 2000000000}
verify(token, b"another-key-" * 4)   -> raises InvalidToken
verify("abc", KEY)                   -> raises InvalidToken
```

PyJWT can read your token with `jwt.decode(token, KEY, algorithms=["HS256"], options={"verify_exp": False})`; the tests check it. The tests import `sign`, `verify` and `InvalidToken`.
