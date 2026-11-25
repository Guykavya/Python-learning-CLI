def coverage(ci_fn, sampler, truth, reps, rng):
    hits = 0
    for _ in range(reps):
        lo, hi = ci_fn(sampler(rng))
        hits += lo <= truth <= hi
    return hits / reps
