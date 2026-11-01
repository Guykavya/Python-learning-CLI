from types import SimpleNamespace


class LegacyTemperatureSensor:
    """Vendor code. Do NOT change this class."""

    def __init__(self, readings):
        self._readings = list(readings)
        self._i = 0

    def read_fahrenheit_string(self):
        text = self._readings[self._i % len(self._readings)]
        self._i += 1
        return text


def monitor(sensor):
    """New code. Works with ANY object that has celsius() -> float."""
    c = sensor.celsius()
    if c >= 30:
        return f"ALERT {c:.1f}C"
    return f"ok {c:.1f}C"


def _to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9


class FahrenheitAdapter:
    def __init__(self, legacy):
        self._legacy = legacy

    def celsius(self):
        text = self._legacy.read_fahrenheit_string().strip()
        return _to_celsius(float(text.rstrip("Ff")))


def adapt_function(read_f):
    return SimpleNamespace(celsius=lambda: _to_celsius(read_f()))
