## Hint 1

Ask "is a car an engine?" (inheritance) and "does a car have an engine?" (composition). With
composition, where does the engine live, and how does `Car.start` reach it?

## Hint 2

Delegation is one line: `self.engine.start()`. Do not check `running` in `Car.start`; the engine
already raises the right error, and it passes through `Car.start` to the caller.

## Hint 3

```
class Engine:
    __init__: horsepower, running = False
    start: if self.running: raise RuntimeError("engine already running"); self.running = True
    stop:  if not self.running: raise RuntimeError("engine not running"); self.running = False

class Car:
    __init__(self, model, engine): model, engine, odometer = 0
    start: self.engine.start()
    stop:  self.engine.stop()
    status: "running" if self.engine.running else "off"
    drive(km): if not self.engine.running: raise ...; self.odometer += km; return self.odometer
```
