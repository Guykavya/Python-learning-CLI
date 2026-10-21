def format_price(amount, currency="Rs", decimals=2, thousands=True):
    """Return amount as text such as 'Rs 1,234.50' or '-Rs 12.00'."""
    spec = ",." if thousands else "."
    digits = format(abs(amount), spec + str(decimals) + "f")
    sign = "-" if amount < 0 else ""
    return sign + currency + " " + digits
