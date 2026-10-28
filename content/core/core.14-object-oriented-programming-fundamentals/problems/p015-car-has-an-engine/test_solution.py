import pytest

from solution import Car, Engine


class FakeEngine:
    """Any object with start(), stop() and running can be a car's engine."""

    def __init__(self):
        self.running = False
        self.calls = []

    def start(self):
        self.calls.append("start")
        self.running = True

    def stop(self):
        self.calls.append("stop")
        self.running = False


def test_engine_starts_off():
    e = Engine(120)
    assert e.horsepower == 120 and e.running is False, "A new Engine stores horsepower and starts with running = False."


def test_engine_start_stop():
    e = Engine(120)
    e.start()
    assert e.running is True, "start() should set running to True."
    e.stop()
    assert e.running is False, "stop() should set running to False."


def test_engine_errors():
    e = Engine(120)
    with pytest.raises(RuntimeError, match="engine not running"):
        e.stop()
    e.start()
    with pytest.raises(RuntimeError, match="engine already running"):
        e.start()
    assert e.running is True, "A failed second start() must leave the engine running."


def test_car_is_not_an_engine():
    assert not issubclass(Car, Engine), "A car HAS an engine; it is not a kind of engine. Do not inherit from Engine."


def test_car_holds_its_engine():
    e = Engine(120)
    car = Car("Nexon", e)
    assert car.model == "Nexon", "Store the model."
    assert car.engine is e, "Store the SAME engine object you were given in self.engine."
    assert car.odometer == 0, "A new car's odometer is 0."


def test_status():
    car = Car("Nexon", Engine(120))
    assert car.status() == "Nexon: off", "Before start, status() is '<model>: off'."
    car.start()
    assert car.status() == "Nexon: running", "After start, status() is '<model>: running'."
    car.stop()
    assert car.status() == "Nexon: off", "After stop, status() is off again."


def test_car_delegates_to_engine():
    fake = FakeEngine()
    car = Car("Test", fake)
    car.start()
    car.stop()
    assert fake.calls == ["start", "stop"], "Car.start() and Car.stop() should call the engine's start() and stop()."


def test_status_reads_the_engine():
    fake = FakeEngine()
    car = Car("Test", fake)
    fake.running = True
    assert car.status() == "Test: running", "status() must ask the engine (self.engine.running), not keep its own copy of the state."


def test_engine_errors_pass_through_the_car():
    car = Car("Nexon", Engine(120))
    car.start()
    with pytest.raises(RuntimeError, match="engine already running"):
        car.start()
    car.stop()
    with pytest.raises(RuntimeError, match="engine not running"):
        car.stop()


def test_drive():
    car = Car("Nexon", Engine(120))
    car.start()
    assert car.drive(15) == 15, "drive(15) from 0 returns the new odometer, 15."
    assert car.drive(5) == 20, "drive adds to the odometer: 15 + 5 = 20."
    assert car.odometer == 20, "drive must change self.odometer."


def test_drive_needs_running_engine():
    car = Car("Nexon", Engine(120))
    with pytest.raises(RuntimeError, match="start the car first"):
        car.drive(3)
    assert car.odometer == 0, "A failed drive must not change the odometer."
    car.start()
    car.drive(10)
    car.stop()
    with pytest.raises(RuntimeError, match="start the car first"):
        car.drive(3)
    assert car.odometer == 10, "After stop, driving is not allowed and the odometer stays 10."


def test_two_cars_have_separate_engines():
    a = Car("A", Engine(100))
    b = Car("B", Engine(100))
    a.start()
    assert b.status() == "B: off", "Each car has its own engine object. Starting one car must not start another."
