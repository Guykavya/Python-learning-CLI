import re

PRICE_RE = re.compile(r"(?:(?<=₹)|(?<=₹ )|(?<=Rs\.)|(?<=Rs\. ))\d[\d,]*(?:\.\d+)?")


def prices(text: str) -> list[float]:
    return [float(s.replace(",", "")) for s in PRICE_RE.findall(text)]
