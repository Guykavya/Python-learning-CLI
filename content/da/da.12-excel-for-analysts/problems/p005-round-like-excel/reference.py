from decimal import Decimal, ROUND_HALF_UP


def xl_round(x, n=0):
    d = Decimal(format(float(x), ".15g"))
    if n >= 0:
        return float(d.quantize(Decimal(1).scaleb(-int(n)), rounding=ROUND_HALF_UP))
    f = Decimal(10) ** -int(n)
    return float((d / f).quantize(Decimal(1), rounding=ROUND_HALF_UP) * f)
