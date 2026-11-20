## Hint 1

Which attack does the timestamp stop, and which attack does the signature stop? Why does the timestamp have to be **inside** the signed text and not just a separate header?

## Hint 2

The signed text is bytes: the encoded `f"{ts}."` followed by `body`. `compare_digest` accepts two `str` objects only when both are ASCII, so what should you do with a signature that contains `é`? Think of converting both sides to bytes first.

## Hint 3

```text
if abs(now - ts) > 300: return "stale"
expected = hmac_sha256(secret, f"{ts}.".encode() + body).hexdigest()
try encode the given signature as ASCII bytes; on failure: "bad signature"
if not compare_digest(expected bytes, given bytes): "bad signature"
return "ok"
```
