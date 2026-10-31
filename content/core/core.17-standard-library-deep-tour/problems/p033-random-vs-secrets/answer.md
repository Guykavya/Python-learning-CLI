**The jobs.**
1. Quiz shuffle with "retry the same quiz": `random.Random(seed)` with a stored seed. Reproducibility
   is the feature; nothing is at stake if a student predicts the order.
2. SMS login code: `secrets` (`secrets.randbelow(10**6)`, zero-padded). It guards an account, so it
   must be unpredictable.
3. Statistics simulation: `random.Random(seed)` with a fixed seed written in the report, so anyone
   can rerun it and get the same graph.
4. Password-reset token: `secrets.token_urlsafe(32)`. Whoever guesses it owns the account.
5. Spreading requests over servers: plain `random` (no seed needed) is fine; predicting it gains
   an attacker nothing. (Round-robin with a counter would also do.)

**Why `random` must not be used for secrets.** It uses the Mersenne Twister, a fast, *deterministic*
algorithm: its whole future is fixed by an internal state of 624 32-bit numbers. Every output is
a simple, reversible function of that state, so an attacker who sees 624 consecutive outputs (for
example a run of tokens) can rebuild the state and compute every later token, and earlier ones
too. Seeding with the time makes it worse: the seed is guessable to within a few seconds, so an
attacker just tries each possible seed. The module is *designed* to be repeatable, which is the
opposite of what a secret needs.

**Why `secrets` is wrong for jobs 1 and 3.** `secrets` reads from the operating system's
cryptographic source and cannot be seeded. You can never get the same sequence again, so "retry
the same quiz" and "the same graph every time" are impossible. It is also slower, though that
rarely matters.

**Why a private `random.Random(seed)`.** The module-level functions share one hidden global
generator with every other module in the program. If a library calls `random.seed(42)`, it resets
that shared state: the application's own "random" choices suddenly repeat on every run, and a
test that depends on call order can break when an unrelated import changes. A private
`rng = random.Random(seed)` gives the library reproducibility without touching anyone else's
generator, and the caller can pass a seed in when it wants repeatable results.
