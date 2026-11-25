import numpy as np


def monty_hall(switch, trials, seed=0):
    rng = np.random.default_rng(seed)
    wins = 0
    for _ in range(trials):
        car = int(rng.integers(3))
        pick = int(rng.integers(3))
        options = [d for d in range(3) if d != pick and d != car]
        opened = int(options[int(rng.integers(len(options)))])
        if switch:
            pick = next(d for d in range(3) if d != pick and d != opened)
        wins += pick == car
    return wins / trials
