## Approach

Look at what the second block adds: elements that were already covered. The answer is right exactly when combining an element with itself changes nothing, `f(x, x) = x`: the operation is **idempotent**.

## Model answer

See `answer.md`.

## What to check

- You named the overlapping positions (3 and 4), not just "some elements".
- You used the word **idempotent** and its equation, and tested each operation with it, including the surprising `xor`.
- You computed the error (`38 - 30 = 8 = 6 + 2`).
- You gave both fixes for sums and their costs.

## Another way

Test the property by brute force: for each operation, compare the two-block answer with the true answer on every range of a few random arrays (chapter section 15, "Checking against brute force"). The idempotent ones never fail; `+`, `*` and `xor` fail on the first range with an overlap.
