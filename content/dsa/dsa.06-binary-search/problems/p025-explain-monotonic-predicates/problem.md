# Explain: is this predicate monotonic?

Binary search on the answer needs a predicate `ok(x)` that is **monotonic**: all `False` values come first and all `True` values after them (or the reverse). Answer in `answer.md`, one short paragraph per item.

For each predicate on whole numbers `x >= 1` say whether it is monotonic. If yes, write its shape (`F...FT...T` or `T...TF...F`) and what you would search for (first True, last True). If not, give two values that break the rule.

1. `x * x >= 50`
2. `x * x <= 50`
3. `x is a prime number`
4. `a ship with capacity x can carry all packages in D days`
5. `the sum of the digits of x is at least 10`
6. `ceil(1000 / x) <= 25`
7. `x is even`

Then answer: **why does a non-monotonic predicate break binary search?** What does one probe at `mid` tell you in the monotonic case?

Read `solution.md` and `answer.md`, and rate your answer.
