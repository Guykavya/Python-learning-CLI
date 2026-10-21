def choose(options, ask=input, tell=print):
    """Ask until the user picks an option by number (from 1) or by name; return it."""
    if not options:
        raise ValueError("options must not be empty")
    prompt = f"Choose 1-{len(options)} or a name: "
    while True:
        text = ask(prompt)
        answer = text.strip()
        try:
            number = int(answer)
        except ValueError:
            for option in options:
                if option.lower() == answer.lower():
                    return option
        else:
            if 1 <= number <= len(options):
                return options[number - 1]
        tell(f"{text!r} is not an option. Type a number from 1 to {len(options)} or a name.")
