from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def to_paise(text):
    # TODO: Decimal, *100, round half up to an int; ValueError for text that is not an amount
    return int(float(text) * 100)


def order_total(lines):
    return 0
