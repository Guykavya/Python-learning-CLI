import pytest

from solution import InstanceCounter, SingletonMeta


def test_singleton_returns_the_same_object():
    class Settings(metaclass=SingletonMeta):
        def __init__(self, debug=False):
            self.debug = debug

    a = Settings(debug=True)
    b = Settings()
    assert a is b, "Every call of a singleton class must return the same object."
    assert isinstance(a, Settings)
    assert b.debug is True, (
        "__init__ must run only on the FIRST call. If debug became False, the second call ran __init__ again."
    )


def test_init_runs_once():
    calls = []

    class Logger(metaclass=SingletonMeta):
        def __init__(self):
            calls.append(1)

    Logger()
    Logger()
    Logger()
    assert len(calls) == 1, f"__init__ ran {len(calls)} times; a singleton creates (and initialises) once."


def test_subclass_gets_its_own_instance():
    class Settings(metaclass=SingletonMeta):
        pass

    class TestSettings(Settings):
        pass

    base = Settings()
    sub = TestSettings()
    assert type(sub) is TestSettings, (
        "TestSettings() returned a Settings object. The subclass found the parent's stored instance through "
        "inheritance (hasattr(cls, ...) or cls._instance). Key the storage by the exact class."
    )
    assert sub is not base
    assert TestSettings() is sub and Settings() is base, "Each class keeps its own single instance."


def test_unrelated_singletons_are_separate():
    class A(metaclass=SingletonMeta):
        pass

    class B(metaclass=SingletonMeta):
        pass

    assert A() is not B() and type(B()) is B, "Two different singleton classes must not share an instance."


def test_failed_init_is_not_remembered():
    class Flaky(metaclass=SingletonMeta):
        attempts = 0

        def __init__(self):
            Flaky.attempts += 1
            if Flaky.attempts == 1:
                raise RuntimeError("first try fails")

    with pytest.raises(RuntimeError):
        Flaky()
    obj = Flaky()
    assert isinstance(obj, Flaky) and Flaky.attempts == 2, (
        "If __init__ raises, no instance may be stored: the next call must try again."
    )


def test_metaclasses_are_metaclasses():
    assert issubclass(SingletonMeta, type) and issubclass(InstanceCounter, type), "Both must subclass type."

    class S(metaclass=SingletonMeta):
        pass

    assert type(S) is SingletonMeta


def test_counter_starts_at_zero_and_counts():
    class Point(metaclass=InstanceCounter):
        def __init__(self, x, y):
            self.x, self.y = x, y

    assert Point.instance_count == 0, "A new class starts with instance_count == 0."
    Point(0, 0)
    Point(1, 1)
    assert Point.instance_count == 2, "Each successful Point(...) adds one."


def test_subclasses_count_separately():
    class Point(metaclass=InstanceCounter):
        pass

    class ColorPoint(Point):
        pass

    assert ColorPoint.instance_count == 0, "Each subclass starts at 0 too (the metaclass runs for every class)."
    Point()
    Point()
    ColorPoint()
    assert Point.instance_count == 2, "Creating a ColorPoint must not change Point.instance_count."
    assert ColorPoint.instance_count == 1, (
        f"ColorPoint.instance_count is {ColorPoint.instance_count}, expected 1. If it is 3, the subclass read "
        "the parent's count through inheritance before adding 1. Give every class its own counter at creation."
    )


def test_subclass_used_first():
    class Point(metaclass=InstanceCounter):
        pass

    class ColorPoint(Point):
        pass

    ColorPoint()
    assert (Point.instance_count, ColorPoint.instance_count) == (0, 1), "Only the class actually called is counted."


def test_failed_creation_is_not_counted():
    class Positive(metaclass=InstanceCounter):
        def __init__(self, n):
            if n <= 0:
                raise ValueError("n must be positive")

    Positive(1)
    with pytest.raises(ValueError):
        Positive(-1)
    assert Positive.instance_count == 1, "Count only after super().__call__ returned: a failed __init__ is not an instance."
