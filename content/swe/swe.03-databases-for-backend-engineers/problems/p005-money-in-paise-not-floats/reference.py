from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def to_paise(text):
    try:
        amount = Decimal(text.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"not an amount: {text!r}") from None
    if not amount.is_finite():
        raise ValueError(f"not an amount: {text!r}")
    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def order_total(lines):
    return sum(qty * unit_paise for qty, unit_paise in lines)
