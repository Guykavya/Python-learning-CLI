import random
from typing import TypeVar

T = TypeVar("T")


def shuffled(items: list[T], seed: int) -> list[T]:
    result = list(items)
    random.Random(seed).shuffle(result)
    return result


def pick_winners(names: list[str], k: int, seed: int) -> list[str]:
    return random.Random(seed).sample(names, k)


def roll_dice(n: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    return [rng.randint(1, 6) for _ in range(n)]


def split_data(items: list[T], test_percent: int, seed: int) -> tuple[list[T], list[T]]:
    if not 0 <= test_percent <= 100:
        raise ValueError("test_percent must be between 0 and 100")
    mixed = shuffled(items, seed)
    n_test = len(mixed) * test_percent // 100
    return mixed[n_test:], mixed[:n_test]
