class TrafficLight:
    NEXT = {"red": "green", "green": "yellow", "yellow": "red"}
    DEFAULT_DURATIONS = {"red": 30, "green": 25, "yellow": 5}

    def __init__(self, start="red", durations=None):
        # TODO: check start and durations, set the state, timer and history
        self._state = start

    # TODO: read-only properties state, time_left, history

    def advance(self):
        return None

    def tick(self, seconds):
        return []

    def emergency(self):
        pass

    def __repr__(self):
        return "TrafficLight()"
