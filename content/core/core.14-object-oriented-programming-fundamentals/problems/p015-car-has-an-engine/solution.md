## Approach

"Is a car an engine?" No. "Does a car have an engine?" Yes. So the car holds an `Engine` object in an
attribute and passes work on to it (chapter section 14, composition and delegation).

- `Car.start()` is one line, `self.engine.start()`. The engine knows its own rules and raises its own
  errors; they travel up through `Car.start` to the caller unchanged.
- `status()` and `drive()` **ask** the engine (`self.engine.running`) instead of keeping a second copy of
  the state, which could get out of step.
- Because `Car` only uses `start()`, `stop()` and `running`, any object with those works: a test's
  `FakeEngine`, or later an `ElectricMotor`. This is duck typing (section 15) and a big reason to prefer
  composition: you can swap the part.

## Code

```python
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower
        self.running = False

    def start(self):
        if self.running:
            raise RuntimeError("engine already running")
        self.running = True

    def stop(self):
        if not self.running:
            raise RuntimeError("engine not running")
        self.running = False


class Car:
    def __init__(self, model, engine):
        self.model = model
        self.engine = engine
        self.odometer = 0

    def start(self):
        self.engine.start()

    def stop(self):
        self.engine.stop()

    def status(self):
        state = "running" if self.engine.running else "off"
        return f"{self.model}: {state}"

    def drive(self, km):
        if not self.engine.running:
            raise RuntimeError("start the car first")
        self.odometer += km
        return self.odometer
```

## Complexity

O(1) for every method.

## Another way

The car could build its own engine: `Car(model, horsepower)` with `self.engine = Engine(horsepower)`
inside `__init__`. That is simpler for the caller, but you can no longer pass in a different engine (or a
fake one for tests). Passing the part in from outside is called *dependency injection*.
