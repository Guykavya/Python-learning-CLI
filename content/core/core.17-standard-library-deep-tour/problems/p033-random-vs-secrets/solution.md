See the model answer shown when you check. The ideas that must appear:

- Jobs 1 and 3: seeded `random.Random(seed)`, because reproducibility is required. Jobs 2 and 4: `secrets`, because an attacker must not predict them. Job 5: plain `random` is fine (nothing to gain by predicting).
- `random` is deterministic (Mersenne Twister): 624 consecutive outputs reveal the whole state, so all later (and earlier) values can be computed; a time-based seed can be brute-forced.
- `secrets` uses the OS cryptographic source, cannot be seeded, so it can never repeat a sequence.
- `random.seed()` changes the global generator shared by the whole program; a library should use its own `random.Random` object (and accept a seed or rng from the caller).
