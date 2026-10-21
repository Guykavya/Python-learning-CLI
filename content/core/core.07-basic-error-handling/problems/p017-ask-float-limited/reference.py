def ask_float(prompt, low, high, ask=input, tell=print, attempts=3):
    """Ask until a number from low to high is given; give up after `attempts` bad answers."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for _ in range(attempts):
        text = ask(prompt)
        try:
            value = float(text)
        except ValueError:
            tell(f"{text!r} is not a number. Type something like {low}.")
            continue
        if low <= value <= high:
            return value
        tell(f"Please choose from {low} to {high}, got {value}.")
    raise ValueError(f"no valid answer after {attempts} attempts")
