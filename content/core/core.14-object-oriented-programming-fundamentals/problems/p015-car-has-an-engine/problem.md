# Composition: a car has an engine

A car is not a kind of engine, so `class Car(Engine)` would be wrong. A car **has** an engine.
That is **composition**: the car keeps an engine object in an attribute and **delegates** work to it
("engine, please start").

Write two classes in `solution.py`:

**`Engine(horsepower)`**
- Stores `horsepower` and an attribute `running`, which starts as `False`.
- `start()` sets `running` to `True`. If it is already running, raise
  `RuntimeError("engine already running")`.
- `stop()` sets `running` to `False`. If it is not running, raise `RuntimeError("engine not running")`.

**`Car(model, engine)`**
- Stores `model`, the engine object in `engine`, and `odometer = 0`.
- `start()` and `stop()` just call the engine's `start()` / `stop()` (the engine's errors pass through).
- `status()` returns `"<model>: running"` or `"<model>: off"`, based on `engine.running`.
- `drive(km)` adds `km` to `odometer` and returns the new odometer value. If the engine is not
  running, raise `RuntimeError("start the car first")` and do not change the odometer.
- `Car` must **not** inherit from `Engine`. It only talks to the engine through `start()`, `stop()`
  and `running`, so any object with those works as an engine.

**Example**

```python
car = Car("Nexon", Engine(120))
print(car.status())       # Nexon: off
car.start()
print(car.status())       # Nexon: running
print(car.drive(15))      # 15
print(car.drive(5))       # 20
car.start()               # RuntimeError: engine already running
car.stop()
car.drive(3)              # RuntimeError: start the car first
```
