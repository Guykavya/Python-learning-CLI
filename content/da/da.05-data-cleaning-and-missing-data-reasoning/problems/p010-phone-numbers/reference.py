import pandas as pd


def clean_phone(s):
    """Ten-digit mobile numbers as text, or missing."""
    digits = s.str.replace(r"\D", "", regex=True)
    digits = digits.str.replace(r"^(?:91|0)(?=[0-9]{10}$)", "", regex=True)
    return digits.where(digits.str.fullmatch(r"[6-9][0-9]{9}", na=False))
