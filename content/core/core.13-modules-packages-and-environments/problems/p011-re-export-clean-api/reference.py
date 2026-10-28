from pathlib import Path

INIT = '''"""unitkit: small unit conversions."""
from .length import to_km, to_miles
from .temperature import to_celsius, to_fahrenheit

__all__ = ["to_miles", "to_km", "to_fahrenheit", "to_celsius"]
__version__ = "1.0.0"
'''

ROUNDING = '''def r2(x):
    return round(x, 2)
'''

LENGTH = '''from ._rounding import r2


def to_miles(km):
    return r2(km * 0.621371)


def to_km(miles):
    return r2(miles * 1.609344)
'''

TEMPERATURE = '''from ._rounding import r2


def to_fahrenheit(c):
    return r2(c * 9 / 5 + 32)


def to_celsius(f):
    return r2((f - 32) * 5 / 9)
'''

FILES = {
    "__init__.py": INIT,
    "_rounding.py": ROUNDING,
    "length.py": LENGTH,
    "temperature.py": TEMPERATURE,
}


def write_unitkit(root):
    pkg = Path(root) / "unitkit"
    pkg.mkdir(parents=True, exist_ok=True)
    for name, text in FILES.items():
        (pkg / name).write_text(text, encoding="utf-8")
