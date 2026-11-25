## Model answer

**Proposal A (`seed + i`).** The output shows the streams **overlap between runs**: run 101's workers 0, 1, 2 produce exactly the numbers of run 100's workers 1, 2, 3. Each worker's stream is fully decided by its integer seed, and the two runs share seven of their eight seeds. If you repeat an experiment with "a different seed" to check that a result is not luck, most of the randomness is in fact the same, so the runs are not independent repetitions. Seeds chosen by arithmetic can also collide in other ways (worker 3 of seed 10 is worker 0 of seed 13). Ch. 13.5 also warns that streams from nearby seeds are not *guaranteed* to be independent.

**Proposal B (one generator copied).** A generator is an object with a **state**. When it is sent to 8 processes, each process gets a copy of the same state, so all 8 workers draw **the same numbers**: 8 identical simulations instead of 8 different ones, and averaging them shrinks nothing. (Inside one process, sharing one generator between threads has the opposite problem: the order of draws depends on timing, so the run is no longer reproducible.)

**Proposal C (`SeedSequence(seed).spawn(8)`).** `spawn` derives 8 child seed sequences from the parent seed by a well-mixed hashing scheme designed for this purpose. The children are **independent streams** that do not overlap with each other or, in practice, with the children of other seeds. The whole set is **reproducible**: the same parent seed always spawns the same 8 children, so running the experiment again with seed 100 gives the same results, worker by worker. (`default_rng(seed).spawn(8)` does the same from a generator, as in Ch. 13.5.)

**What each worker does.** Each worker receives its own generator once, keeps it for the whole job, and draws everything from it (passing it into functions as an argument, Ch. 13.2). It must not create new generators with fixed seeds inside loops (that repeats numbers), must not use the global `np.random.seed` functions, and must not share or reuse one generator across workers. Record the parent seed and the NumPy version with the results.

**Checklist: your answer should mention**
- [ ] A: `seed + i` makes runs with nearby seeds share streams (the output shows the shift)
- [ ] B: copies of one generator have the same **state**, so every worker draws the same numbers; do not reuse a generator across workers
- [ ] C: **spawn** derives **independent streams** from one seed
- [ ] C is **reproducible**: same parent seed, same children
- [ ] each worker keeps and passes around its own generator; no global seeding
