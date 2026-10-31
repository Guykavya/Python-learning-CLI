import random


def draw_winners(entries, k, rng=None):
    return random.sample(entries, k)


def roll_dice(count, rng=None):
    return [random.randint(1, 6) for _ in range(count)]
