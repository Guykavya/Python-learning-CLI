- Calling `random.sample(...)` (the module function): it uses the shared global generator, so seeding
  your `rng` has no effect.
- Using `rng.shuffle(entries)` and slicing: it **changes the caller's list**.
- A mutable default `rng=random.Random()` in the signature: created once, shared by all calls.
- Drawing the numbers in a different order than the spec: the seeded expectation then differs.
- Testing random code with "run it 100 times and hope". Seed it, or test properties (length, range).
