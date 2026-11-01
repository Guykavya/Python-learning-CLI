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


class FahrenheitAdapter:
    pass


def adapt_function(read_f):
    raise NotImplementedError
