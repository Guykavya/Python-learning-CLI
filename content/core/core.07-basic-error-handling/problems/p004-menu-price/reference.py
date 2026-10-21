def price_message(menu, item):
    """Return a customer-friendly sentence about the price of item."""
    try:
        price = menu[item]
    except KeyError:
        if not menu:
            return f"Sorry, {item!r} is not on the menu. The menu is empty today."
        return f"Sorry, {item!r} is not on the menu. Choose one of: {', '.join(sorted(menu))}."
    else:
        return f"{item} costs Rs {price}"
