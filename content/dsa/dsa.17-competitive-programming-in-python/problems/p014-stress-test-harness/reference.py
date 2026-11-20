import copy
import random


def _call(f, case):
    try:
        return f(*copy.deepcopy(case))
    except Exception as e:
        return e


def _same(a, b):
    if isinstance(a, Exception) or isinstance(b, Exception):
        return isinstance(a, Exception) and isinstance(b, Exception) and type(a) is type(b)
    return a == b


def stress(fast, brute, gen, trials=1000, seed=1):
    rng = random.Random(seed)
    for _ in range(trials):
        case = gen(rng)
        a = _call(fast, case)
        b = _call(brute, case)
        if not _same(a, b):
            return case, a, b
    return None
