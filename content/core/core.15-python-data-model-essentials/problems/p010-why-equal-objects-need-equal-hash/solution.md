## Approach

Equal objects must be found in the same bucket, so equal objects need equal hashes. Mia compares numbers but hashes text, which breaks the contract. Follow the lookup step by step to see where the search goes wrong.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Prove it in the REPL: build the set, print `len(seen)`, `Version('1.00') in seen`, and `any(v == Version('1.00') for v in seen)`; the last one is `True`, which shows that only the hash step failed.
