See the model answer shown when you check. The ideas that must appear:

1. A test calls the code with a chosen input and `assert`s the output equals the expected output.
2. Reasons: two tries miss edge cases; hand checks are slow, forgotten and unrepeatable; a later change can cause a regression that nobody notices; tests document what the function should do.
3. Cost: time to write and keep up to date; payoff: instant, repeatable proof after every change.
4. A passing suite does not prove the code is correct for untested inputs, nor that the tests themselves are right.
