import random
from datetime import datetime


def make_greeting(name):
    hour = datetime.now().hour
    if hour < 12:
        return f"Good morning, {name}"
    if hour < 18:
        return f"Good afternoon, {name}"
    return f"Good evening, {name}"


def is_expired(token):
    return datetime.now() >= token["expires"]


def pick_tip(tips):
    return random.choice(tips)


def save_report(rows, path):
    with open(path, "w") as f:
        for name, score in rows:
            f.write(f"{name},{score}\n")
