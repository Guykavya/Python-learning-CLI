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
