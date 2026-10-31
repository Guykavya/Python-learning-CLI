## Hint 1

`secrets.token_urlsafe(n)` returns a str built from `n` random bytes; `secrets.choice(seq)` picks
one item. For the password, how can you **guarantee** one character of each kind instead of
hoping that a random pick contains them?

## Hint 2

Pick one lowercase, one uppercase, one digit and one symbol first, then fill the rest from the
full alphabet. Now the first four positions are predictable: shuffle the list with a secure
shuffler, `secrets.SystemRandom().shuffle(chars)`. For `same_secret`, `compare_digest` accepts
`bytes`; what does `"café".encode("utf-8")` give?

## Hint 3

```
make_token:    if nbytes < 16: raise ValueError;  return secrets.token_urlsafe(nbytes)
make_password: if length < 8: raise ValueError
               chars = [choice(lower), choice(upper), choice(digits), choice(SYMBOLS)]
               chars += [choice(ALPHABET) for the remaining length - 4]
               SystemRandom().shuffle(chars);  return "".join(chars)
same_secret:   return compare_digest(given.encode("utf-8"), expected.encode("utf-8"))
```
