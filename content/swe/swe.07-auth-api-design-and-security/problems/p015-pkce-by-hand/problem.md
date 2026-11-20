# PKCE by hand

Chapter section 5.2 (authorization code flow with PKCE). PKCE protects the authorization **code** while it travels through the browser. The client invents a secret `code_verifier` and sends only its hash, the `code_challenge`, at the start. At the token step it sends the verifier itself. A thief who stole the code cannot use it without the verifier.

Write two functions in `solution.py`:

- `make_verifier() -> str`: a random verifier of **43 to 128 characters** from the set `A-Z a-z 0-9 - . _ ~`. Use `secrets`.
- `challenge_for(verifier: str) -> str`: the **S256** challenge: `BASE64URL(SHA256(verifier))`, where BASE64URL is the URL-safe base64 alphabet **without** `=` padding. A verifier outside the allowed length or alphabet raises `ValueError`.

## Example

This is the test vector of RFC 7636 appendix B:

```python
challenge_for("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk")
# 'E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM'
```

The challenge always has 43 characters (32 bytes of SHA-256, encoded).
