def build_profile(name, **details):
    """Return a new dict with 'name' first, then every detail whose value is not None."""
    profile = {"name": name}
    for key, value in details.items():
        if value is not None:
            profile[key] = value
    return profile
