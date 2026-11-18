## Approach

Both functions are the same loop: compute both answers, compare, stop at the first difference. The care is in three details:

1. **Copies.** A list instance is copied before each call, so a greedy that sorts in place cannot change what the brute force sees, or what we report.
2. **Stop early.** Return as soon as a difference appears. The first counterexample is usually the smallest one when the instances grow, and later instances may be expensive.
3. **One seeded generator.** `random.Random(seed)` is created once. The instances then depend only on `seed`, `trials` and `make_input`, so the same call finds the same counterexample every time.

```python
import random


def fresh(instance):
    """Each call gets its own copy of a list, so in-place sorting cannot leak out."""
    return list(instance) if isinstance(instance, list) else instance


def first_counterexample(greedy, brute, instances):
    for instance in instances:
        if greedy(fresh(instance)) != brute(fresh(instance)):
            return instance
    return None


def stress_test(greedy, brute, make_input, trials=1000, seed=0):
    rng = random.Random(seed)
    for _ in range(trials):
        instance = make_input(rng)
        g = greedy(fresh(instance))
        b = brute(fresh(instance))
        if g != b:
            return (instance, g, b)
    return None
```

`list(instance)` is a **shallow** copy: it protects the order of the list (what `sort` changes), not objects inside it. For lists of tuples or numbers that is all that can change.

## How to use it

1. Write the greedy and the simplest possible brute force (all subsets, all orders, DP).
2. Write `make_input(rng)` with **tiny** sizes (3 to 8 items) and a **small range** of values, so ties and duplicates are common.
3. Run `stress_test`. A returned tuple is a proof that the greedy is wrong; `None` is evidence, not a proof (chapter section 15).
4. When it fails, shrink the instance by hand to the smallest one that still fails, and try to understand *why* in one sentence.

## Complexity

`trials` times the cost of one greedy call plus one brute-force call. The brute force dominates; that is why the instances must stay tiny.

## Another way

`stress_test` can reuse `first_counterexample` by passing it a generator of instances: `first_counterexample(greedy, brute, (make_input(rng) for _ in range(trials)))`. The generator creates instances lazily, so it still stops early. You then have to compute the two answers once more to report them, which is why the version above keeps its own loop.
