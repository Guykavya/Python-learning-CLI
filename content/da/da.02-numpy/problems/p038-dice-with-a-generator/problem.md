# Dice with a Generator

Chapter sections 13.1–13.2 and 13.6. Write `simulate_rolls(n, rng)`: roll a fair six-sided die `n` times using the **Generator `rng` that is passed in**, and return how many times each face came up.

- Return an integer array of length 6: element 0 counts the 1s, element 5 counts the 6s. The counts add up to `n`. `n = 0` gives six zeros.
- Use only `rng` for randomness: no `np.random.seed`, no `np.random.randint`, no `np.random.default_rng(...)` inside the function. The test checks that two generators made with the same seed give the same counts, that the global legacy state does not matter, and that calling twice with the **same** `rng` gives two different sets of rolls (the generator moves on).
- No Python loop over the rolls.

## Example

```python
rng = np.random.default_rng(123)
counts = simulate_rolls(600, rng)
counts.shape, int(counts.sum())
# ((6,), 600)
# each of the six counts is close to 100; the exact numbers depend on the seed and the NumPy version
```
