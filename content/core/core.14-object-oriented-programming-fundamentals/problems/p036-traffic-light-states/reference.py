class TrafficLight:
    NEXT = {"red": "green", "green": "yellow", "yellow": "red"}
    DEFAULT_DURATIONS = {"red": 30, "green": 25, "yellow": 5}

    def __init__(self, start="red", durations=None):
        if durations is None:
            durations = self.DEFAULT_DURATIONS
        if sorted(durations) != ["green", "red", "yellow"]:
            raise ValueError("durations needs exactly the keys 'red', 'green' and 'yellow'")
        for colour, seconds in durations.items():
            if not isinstance(seconds, int) or seconds < 1:
                raise ValueError(f"duration of {colour} must be a whole number of at least 1, got {seconds!r}")
        if start not in self.NEXT:
            raise ValueError(f"start must be 'red', 'green' or 'yellow', got {start!r}")
        self._durations = dict(durations)
        self._state = start
        self._time_left = self._durations[start]
        self._history = [start]

    @property
    def state(self):
        return self._state

    @property
    def time_left(self):
        return self._time_left

    @property
    def history(self):
        return list(self._history)

    def advance(self):
        self._state = self.NEXT[self._state]
        self._time_left = self._durations[self._state]
        self._history.append(self._state)
        return self._state

    def tick(self, seconds):
        if not isinstance(seconds, int) or seconds < 0:
            raise ValueError(f"seconds must be a whole number of at least 0, got {seconds!r}")
        entered = []
        while seconds >= self._time_left:
            seconds -= self._time_left
            entered.append(self.advance())
        self._time_left -= seconds
        return entered

    def emergency(self):
        if self._state != "red":
            self._state = "red"
            self._history.append("red")
        self._time_left = self._durations["red"]

    def __repr__(self):
        return f"TrafficLight(state={self._state!r}, time_left={self._time_left})"
