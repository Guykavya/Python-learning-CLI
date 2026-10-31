class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower
        self.running = False

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class Car:
    def __init__(self, model, engine):
        # TODO: store model, the engine object, and odometer = 0
        pass

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError

    def drive(self, km):
        raise NotImplementedError
