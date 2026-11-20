## Hint 1

Go through the six tokens one at a time. For each, ask **which line of the program sees the problem first**: the `kid` lookup, the algorithm list, the signature, or the claims? A token is only checked against the next rule if it passed the one before.

## Hint 2

The order inside `verify` is: (1) look at the `kid` in the header; (2) `jwt.decode` checks `alg` against `["HS256"]`, then the signature with the key, then the claims (`exp`, `aud`, `iss`, required names). Token 4 uses an HS256 header (so the algorithm is fine) but another secret: which check fails? Token 6 has a perfect signature: why does it still not get that far?

## Hint 3

```text
1 exp in 2001, otherwise perfect           -> claims check: exp
2 alg "none", no signature                 -> algorithm not in ["HS256"]: alg
3 everything right                         -> accepted
4 HS256 but another secret                 -> signature
5 aud "reports"                            -> claims check: aud
6 kid "../../etc/passwd" not in KEYS       -> stopped before decoding: kid
```
