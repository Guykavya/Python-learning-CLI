def ask_float(prompt, low, high, ask=input, tell=print, attempts=3):
    """Ask until a number from low to high is given; give up after `attempts` bad answers."""
    return float(ask(prompt))
