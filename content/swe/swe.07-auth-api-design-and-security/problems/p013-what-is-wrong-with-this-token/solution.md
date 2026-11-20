## Approach

Follow each token through `verify`, which checks in this order: the `kid`, then PyJWT's algorithm check, then the signature, then the claims.

```text
1: exp
2: alg
3: accepted
4: signature
5: aud
6: kid
```

- **1: `exp`.** Signature and algorithm are fine, so PyJWT goes on to the claims. `exp = 1_000_000_000` is September 2001: expired. (Chapter 4.2: always check `exp`.)
- **2: `alg`.** The header says `none` and the signature is empty. The verifier lists `algorithms=["HS256"]`, so PyJWT raises `InvalidAlgorithmError` before it looks at anything else. The chapter's `vulnerable_verify` accepts the same token because of the line `alg = json.loads(...)["alg"]`, which lets the token choose the algorithm. (Chapter 4.3, attack 1.)
- **3: `accepted`.** Right key, right algorithm, `aud` and `iss` match, `exp` is in 2096.
- **4: `signature`.** The header says HS256, so the algorithm check passes. But the token was signed with the text of a "public key", not the server's secret: the recomputed HMAC does not match, `InvalidSignatureError`. This is the failed form of **algorithm confusion** (attack 2). A verifier that accepted several algorithms for one key could be fooled into using a public key as an HMAC secret. The defence is the same rule: one algorithm per key, fixed in code.
- **5: `aud`.** Signature and `exp` are fine; the token was meant for the `reports` service, and this verifier is `payments`: `InvalidAudienceError`.
- **6: `kid`.** The header names a key id that is not in `KEYS`, so the verifier stops before decoding. The token is otherwise perfect, which shows the point: the `kid` comes from the attacker, so it may only **select** among keys you already hold (a dictionary lookup). If a server used it as a file name (`open("keys/" + kid)`) or in a query, `../../etc/passwd` would become path traversal or SQL injection (chapters 14.3 and 14.5).

How the output was obtained: the program in `problem.md` was worked out by hand first (the six answers above), then run with Python 3.14 and PyJWT 2.15.1; the printed lines are identical, and are the contents of `expected.txt`. The tokens in the program are real values built by `jwt.encode` or by hand; the output does not depend on the date until the valid token's `exp` (year 2096) passes.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Print the **exception class** instead of a word (`type(exc).__name__`): `ExpiredSignatureError`, `InvalidAlgorithmError`, `InvalidSignatureError`, `InvalidAudienceError`. It is how you would debug a real verifier. In production you do the opposite for the *client*: they get one generic "invalid token" answer, and only your log keeps the reason (chapter 15.7).
