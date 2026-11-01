import random
from datetime import datetime


def make_greeting(name, now=datetime.now):
    hour = now().hour
    if hour < 12:
        return f"Good morning, {name}"
    if hour < 18:
        return f"Good afternoon, {name}"
    return f"Good evening, {name}"


def is_expired(token, now=datetime.now):
    return now() >= token["expires"]


def pick_tip(tips, rng=random):
    return rng.choice(tips)


def save_report(rows, path, opener=open):
    with opener(path, "w") as f:
        for name, score in rows:
            f.write(f"{name},{score}\n")
