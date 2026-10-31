- Writing `class Car(Engine)`. A car would then *be* an engine: `car.horsepower`, `car.running` and the
  engine's methods leak into the car's interface.
- Keeping a separate `self.running` in `Car`. If someone uses the engine directly, the car's copy is wrong.
- Catching the engine's `RuntimeError` in `Car.start` and printing it. The caller then cannot tell that
  starting failed.
- Creating `Engine(...)` inside `Car.__init__` and ignoring the `engine` argument.
- Adding km before checking that the engine runs.
