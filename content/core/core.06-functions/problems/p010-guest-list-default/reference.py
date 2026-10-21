def invite(name, guests=None):
    """Append name to guests (a new list if none is given) and return the list."""
    if guests is None:
        guests = []
    guests.append(name)
    return guests
