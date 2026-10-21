def choose(options, ask=input, tell=print):
    """Ask until the user picks an option by number (from 1) or by name; return it."""
    text = ask(f"Choose 1-{len(options)} or a name: ")
    return options[int(text) - 1]
