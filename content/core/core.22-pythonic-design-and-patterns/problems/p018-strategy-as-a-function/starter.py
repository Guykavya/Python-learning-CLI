def checkout(items, discount="none"):
    total = sum(items)
    if discount == "none":
        pass
    elif discount == "ten":
        total = total - total * 10 / 100
    elif discount == "twenty":
        total = total - total * 20 / 100
    elif discount == "five_off":
        total = max(total - 5, 0)
    else:
        raise ValueError(f"unknown discount: {discount}")
    return round(total, 2)
