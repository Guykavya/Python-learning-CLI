## Hint 1

What does `secrets.token_urlsafe(n)` return, and which characters can it contain? Are they all legal in a verifier? How many characters do you get from `n` bytes?

## Hint 2

SHA-256 gives 32 **bytes**. Which function of `base64` uses `-` and `_`? What does it add at the end, and which method removes it? Remember to turn the verifier text into bytes first.

## Hint 3

```text
make_verifier: return secrets.token_urlsafe(48)        # 64 characters
challenge_for(v):
    check v matches [A-Za-z0-9-._~]{43,128}, else ValueError
    digest = sha256(v as ascii bytes).digest()
    return urlsafe_b64encode(digest) without trailing '=' as str
```
