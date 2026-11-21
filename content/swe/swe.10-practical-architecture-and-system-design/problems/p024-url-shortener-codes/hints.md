## Hint 1

Split the work. `encode`/`decode` are the base-62 conversion (repeated `divmod` by 62; `index` in the alphabet). For `Shortener`, think of one dictionary keyed by the **lower-cased** code: it answers "is this taken?" and "resolve" with one lookup, whether the code is an alias or a generated one. What does the counter do when its next code is already in that dictionary?

## Hint 2

```text
create(url, alias):
    if alias is given: validate (regex 3-32 of [A-Za-z0-9_-]) -> InvalidAlias; reserved (lower-case) -> InvalidAlias; taken (lower-case) -> AliasTaken; store; return alias
    else: loop: code = encode(counter).rjust(7, "0"); counter += 1; if code.lower() not taken: store; return code
resolve(code): urls.get(code.lower())
```
A failed alias returns before the counter is touched, so nothing is burnt.
