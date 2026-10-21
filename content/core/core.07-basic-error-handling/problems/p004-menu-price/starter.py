def price_message(menu, item):
    """Return a customer-friendly sentence about the price of item."""
    return item + " costs Rs " + str(menu[item])
