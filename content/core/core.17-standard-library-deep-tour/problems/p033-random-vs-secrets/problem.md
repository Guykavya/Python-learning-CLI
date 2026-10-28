# Explain: random or secrets?

Both modules give "random numbers", yet using the wrong one is either a security hole or a test
that fails one time in a hundred. Look at these five jobs:

1. Shuffling the questions in a quiz app, so that a student can press "retry the same quiz".
2. The 6-digit one-time code sent by SMS for a bank login.
3. A simulation for a statistics assignment that must give the same graph every time the teacher runs it.
4. The "reset your password" link sent by e-mail (`https://site/reset?token=...`).
5. Choosing which of 3 servers handles the next web request, spread evenly.

In `answer.md` (about 200 to 350 words):

- For each job say `random` (with or without a seed) or `secrets`, and why.
- Explain what makes `random` unsuitable for secrets. (How does the Mersenne Twister work, what
  can an attacker learn from its outputs, and what does seeding with the current time do?)
- Explain why `secrets` is unsuitable for jobs 1 and 3.
- Explain why a library function should use its own `random.Random(seed)` instead of calling
  `random.seed(...)` itself.

**Example** of the kind of reasoning wanted, for a job not on the list: *"A dice roll in a board
game app: `random`, no seed. Nothing is at stake if someone predicts it, and speed and
simplicity matter more than unpredictability."*
