import random


def draw_winners(entries, k, rng=None):
    if rng is None:
        rng = random.Random()
    if k < 0 or k > len(entries):
        raise ValueError("k must be between 0 and len(entries)")
    return rng.sample(entries, k)


def roll_dice(count, rng=None):
    if rng is None:
        rng = random.Random()
    if count < 0:
        raise ValueError("count must not be negative")
    return [rng.randint(1, 6) for _ in range(count)]
