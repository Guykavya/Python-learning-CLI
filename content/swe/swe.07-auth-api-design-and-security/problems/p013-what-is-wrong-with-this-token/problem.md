# What is wrong with this token?

Chapter section 4.3 (attacks on JWT you must be able to explain), 4.2 (claims that must be checked) and "Try it: what is wrong with this token?". Below is a verifier and six tokens. The verifier tells you **which check rejects a token**, or says `accepted`. For each token, predict the line the program prints.

```python
import base64
import json
import warnings

import jwt

warnings.simplefilter("ignore")           # PyJWT warns about short demo keys; ours are long

KEY = b"a-long-random-demo-key-of-at-least-32-bytes!"
PUBLIC_TEXT = "pagebound-public-key-text-anyone-can-download-0123456789"
KEYS = {"k1": KEY}                        # key id -> secret; only "k1" exists

GOOD = {"sub": "42", "iss": "pagebound-auth", "aud": "payments", "exp": 4_000_000_000}


def b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def verify(token: str) -> str:
    """Return the name of the check that rejects the token, or 'accepted'."""
    header = jwt.get_unverified_header(token)
    kid = header.get("kid", "k1")
    if kid not in KEYS:
        return "kid"
    try:
        jwt.decode(token, KEYS[kid], algorithms=["HS256"], audience="payments",
                   issuer="pagebound-auth", options={"require": ["exp", "sub", "iss", "aud"]})
    except jwt.InvalidAlgorithmError:
        return "alg"
    except jwt.InvalidSignatureError:
        return "signature"
    except jwt.ExpiredSignatureError:
        return "exp"
    except jwt.InvalidAudienceError:
        return "aud"
    return "accepted"


tokens = [
    jwt.encode({**GOOD, "exp": 1_000_000_000}, KEY, algorithm="HS256"),
    b64u(json.dumps({"alg": "none", "typ": "JWT"}).encode()) + "." + b64u(json.dumps(GOOD).encode()) + ".",
    jwt.encode(GOOD, KEY, algorithm="HS256"),
    jwt.encode(GOOD, PUBLIC_TEXT, algorithm="HS256"),
    jwt.encode({**GOOD, "aud": "reports"}, KEY, algorithm="HS256"),
    jwt.encode(GOOD, KEY, algorithm="HS256", headers={"kid": "../../etc/passwd"}),
]

for number, token in enumerate(tokens, start=1):
    print(f"{number}: {verify(token)}")
```

The six tokens, in words (all of them have the same claims except where it says so):

1. a correctly signed token whose `exp` is in the year 2001;
2. a token whose header says `{"alg": "none"}` and has **no** signature;
3. a correctly signed token with good claims;
4. a token signed with HS256, but using a **different** secret (the text of a public key that anyone can download) instead of the server's key;
5. a correctly signed token whose `aud` is `"reports"`;
6. a correctly signed token whose header carries `"kid": "../../etc/passwd"` (a path, as an attacker would try if a server loaded key files by id).

The verifier returns one of five words, and these are the only words allowed:

| Word | Meaning |
|---|---|
| `kid` | the key id in the header is not one of our keys |
| `alg` | the algorithm in the header is not allowed (`algorithms=["HS256"]`) |
| `signature` | the signature does not match the payload |
| `exp` | the token has expired |
| `aud` | the token is for another audience |
| `accepted` | the verifier accepts the token |

Every token has **exactly one** defect (or none), so each answer is one word. Think about which check sees the defect: the program first reads the header, then PyJWT checks the algorithm, then the signature, then the claims.

## What to write

Write six lines, in the form `<number>: <word>`, as the program would print them. **Do not run it.**

## After you answer

- Token 4 is the "algorithm confusion" idea (chapter 4.3, attack 2). Why does it fail here, and what must a verifier that supports RS256 **and** HS256 do to be safe?
- Token 2 would be accepted by the chapter's `vulnerable_verify`. Which line of that function causes it?
- Why is a `kid` that is used to open a file, or to build an SQL query, dangerous? What does our `KEYS` dictionary do instead?
