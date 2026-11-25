import math

MISSING = {"", "na", "n/a", "nan", "null", "none", "-", "?"}


def parse_number(text):
    t = text.strip().lower()
    if t in MISSING:
        return None
    for junk in ("rs.", "rs", "ms", "%", "$"):
        t = t.replace(junk, "")
    t = t.replace(",", "").replace(" ", "")
    try:
        x = float(t)
    except ValueError:
        raise ValueError(f"cannot parse {text!r}") from None
    if not math.isfinite(x):
        raise ValueError(f"cannot parse {text!r}")
    return x
