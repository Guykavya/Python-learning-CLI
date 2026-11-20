## Hint 1

`first_counterexample` is one loop with an early `return`. Two details: how do you protect the instance from a greedy that sorts it (look at "The copy rule"), and what do you return after the loop?

## Hint 2

For the copy rule, a small helper keeps both functions short:

```
def fresh(instance):
    return list(instance) if instance is a list else instance
```

Call `greedy(fresh(instance))` and `brute(fresh(instance))`, so each one gets its own copy, and the variable `instance` keeps the original.

## Hint 3

```
def stress_test(greedy, brute, make_input, trials=1000, seed=0):
    rng = random.Random(seed)              # once, outside the loop
    for _ in range(trials):
        instance = make_input(rng)
        g = greedy(fresh(instance))
        b = brute(fresh(instance))
        if g != b:
            return (instance, g, b)
    return None
```

Creating `random.Random(seed)` inside the loop would give the **same** instance in every trial: 1000 trials that test one input.
