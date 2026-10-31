def make_noise(things):
    results = []
    for thing in things:
        try:
            speak = thing.speak
        except AttributeError:
            continue
        results.append(speak())
    return results
