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
