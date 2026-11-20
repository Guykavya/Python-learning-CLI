import json
import random


def jittered(seconds, rng):
    # TODO: between 90% and 110% of seconds
    return seconds


def get_swr(cache, key, loader, now, soft=60, hard=600, rng=random.random):
    # TODO: cold miss / fresh / refreshed / stale
    return loader(key), "cold miss"
