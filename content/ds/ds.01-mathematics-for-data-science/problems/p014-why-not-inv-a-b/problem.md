# Why not inv(A) @ b?

Chapter section 3.7. Many tutorials write `x = np.linalg.inv(A) @ b`. The chapter says to write `x = np.linalg.solve(A, b)` instead.

In `answer.md` explain, in about 150 to 250 words, **why `solve` is better** than computing the inverse, covering:

1. the amount of work (what is computed and what is thrown away);
2. the accuracy;
3. the case of **many right-hand sides** `b1, b2, ...` for the same `A`, and how you would time the two approaches fairly (the chapter's `best_of` helper takes the best of several repeats).

## Example

A start: "`inv(A)` computes all `n` columns of the inverse, but the question only needs one vector `x`..."
