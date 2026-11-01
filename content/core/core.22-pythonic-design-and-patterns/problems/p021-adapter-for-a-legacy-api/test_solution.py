import pytest

from solution import FahrenheitAdapter, LegacyTemperatureSensor, adapt_function, monitor


def test_conversion_values():
    sensor = FahrenheitAdapter(LegacyTemperatureSensor(["212F", "32F", "-40F", "72.5F"]))
    assert sensor.celsius() == pytest.approx(100.0), "212F is 100C. Formula: (F - 32) * 5 / 9."
    assert sensor.celsius() == pytest.approx(0.0), "32F is 0C."
    assert sensor.celsius() == pytest.approx(-40.0), "-40F is -40C."
    assert sensor.celsius() == pytest.approx(22.5), "72.5F is 22.5C."


def test_each_call_reads_the_sensor_again():
    legacy = LegacyTemperatureSensor(["32F", "212F"])
    adapter = FahrenheitAdapter(legacy)
    assert [adapter.celsius(), adapter.celsius()] == [pytest.approx(0.0), pytest.approx(100.0)], (
        "celsius() must call read_fahrenheit_string() every time; do not read once in __init__ and keep the value."
    )


def test_messy_text_is_accepted():
    adapter = FahrenheitAdapter(LegacyTemperatureSensor([" 68.0F\n", "68f"]))
    assert adapter.celsius() == pytest.approx(20.0), "Surrounding whitespace must be ignored."
    assert adapter.celsius() == pytest.approx(20.0), "A lowercase 'f' suffix is accepted too."


def test_the_new_code_works_with_the_adapter():
    adapter = FahrenheitAdapter(LegacyTemperatureSensor(["72.5F", "95F"]))
    assert monitor(adapter) == "ok 22.5C", "72.5F is 22.5C, below the alert level, so monitor reports ok."
    assert monitor(adapter) == "ALERT 35.0C", "95F is 35C, which is at or above the alert level of 30."


def test_monitor_is_duck_typed():
    class Fixed:
        def celsius(self):
            return 30.0

    assert monitor(Fixed()) == "ALERT 30.0C", "monitor must accept any object with celsius(); do not check types."


def test_function_adapter():
    values = iter([32.0, 86.0])
    sensor = adapt_function(lambda: next(values))
    assert sensor.celsius() == pytest.approx(0.0), "adapt_function(read_f).celsius() converts what read_f() returns."
    assert sensor.celsius() == pytest.approx(30.0), "Call read_f again on every celsius() call."
    assert monitor(adapt_function(lambda: 50.0)) == "ok 10.0C", "The function adapter works with monitor too."


def test_legacy_class_was_not_modified():
    public = {
        name
        for name, value in vars(LegacyTemperatureSensor).items()
        if not (name.startswith("__") and name.endswith("__"))
    }
    assert public == {"read_fahrenheit_string"}, (
        f"LegacyTemperatureSensor now has {sorted(public)}. It is vendor code: wrap it in an adapter, do not add methods to it."
    )
    assert not hasattr(LegacyTemperatureSensor, "celsius"), "Do not give the legacy class a celsius() method."
    legacy = LegacyTemperatureSensor(["32F"])
    FahrenheitAdapter(legacy).celsius()
    assert "celsius" not in vars(legacy), "Do not attach celsius to the legacy object (no monkeypatching)."


def test_adapter_is_not_a_subclass():
    assert LegacyTemperatureSensor not in FahrenheitAdapter.__mro__, (
        "Wrap the legacy object (composition): FahrenheitAdapter should not inherit from LegacyTemperatureSensor."
    )
