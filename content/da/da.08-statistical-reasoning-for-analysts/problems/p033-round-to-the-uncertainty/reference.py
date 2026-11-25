import math


def sig_round(value, ref):
    if ref == 0 or not math.isfinite(ref):
        return f"{value:,.0f}"
    decimals = max(0, 1 - math.floor(math.log10(abs(ref))))
    return f"{round(value, decimals):,.{decimals}f}"
