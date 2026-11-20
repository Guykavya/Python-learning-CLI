# Verify a signed webhook

Chapter section 6.4 (signed webhooks). A payment provider calls your server (`POST /hooks/payment`). You must be sure that the call really comes from the provider, that nobody changed the body, and that nobody recorded an old call to send it again.

The provider sends the raw body and two headers: the timestamp `ts` (whole seconds) and the `signature`, which is the hex digest of `HMAC-SHA256(secret, f"{ts}." + body)` (the text `ts`, a dot, then the body bytes).

Write `receive(body: bytes, ts: int, signature: str, now: int, secret: bytes) -> str` in `solution.py`. It returns exactly one of:

- `"stale"`: the timestamp is more than **300 seconds** away from `now` (in either direction; exactly 300 is fine). Check this **first**.
- `"bad signature"`: the signature does not match. Compare with `hmac.compare_digest`. Any text is possible as a signature (empty, not hex, non-ASCII): answer `"bad signature"`, never raise.
- `"ok"`: everything fits.

Work with the **raw bytes** you received. Do **not** parse the JSON and dump it again before checking: the spacing and the key order may change, and the signature no longer fits. `now` is given; do not read the clock.

## Example

```python
body = b'{"id": "evt_1", "amount": 500}'
sig = hmac.new(b"whsec", b"1700000000." + body, hashlib.sha256).hexdigest()
receive(body, 1700000000, sig, 1700000100, b"whsec")      # 'ok'
receive(body, 1700000000, sig, 1700000301, b"whsec")      # 'stale'
receive(body.replace(b"500", b"900"), 1700000000, sig, 1700000100, b"whsec")   # 'bad signature'
```

(Remembering event ids to ignore duplicates, as in the chapter, is a separate step and not part of this problem.)
