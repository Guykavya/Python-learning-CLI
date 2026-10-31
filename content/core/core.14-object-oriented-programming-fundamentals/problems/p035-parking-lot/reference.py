class ParkingError(Exception):
    """Base class for every parking lot error."""


class LotFullError(ParkingError):
    def __init__(self, size):
        self.size = size
        super().__init__(f"no free spot for a {size} car")


class AlreadyParkedError(ParkingError):
    def __init__(self, plate, spot):
        self.plate = plate
        self.spot = spot
        super().__init__(f"{plate} is already parked at {spot}")


class NotParkedError(ParkingError):
    def __init__(self, plate):
        self.plate = plate
        super().__init__(f"{plate} is not parked here")


SIZES = ("small", "large")


def _clean(plate):
    return plate.strip().upper()


class ParkingLot:
    def __init__(self, small, large):
        for count in (small, large):
            if not isinstance(count, int) or count < 0:
                raise ValueError(f"spot counts must be whole numbers of at least 0, got {count!r}")
        # spot name -> plate or None, in order S1..Sn then L1..Lm
        self._spots = {}
        for i in range(1, small + 1):
            self._spots[f"S{i}"] = None
        for i in range(1, large + 1):
            self._spots[f"L{i}"] = None
        self._where = {}          # plate -> spot name

    def _first_free(self, prefix):
        for name, plate in self._spots.items():
            if name.startswith(prefix) and plate is None:
                return name
        return None

    def park(self, plate, size):
        if size not in SIZES:
            raise ValueError(f"size must be 'small' or 'large', got {size!r}")
        plate = _clean(plate)
        if plate in self._where:
            raise AlreadyParkedError(plate, self._where[plate])
        spot = self._first_free("L") if size == "large" else (self._first_free("S") or self._first_free("L"))
        if spot is None:
            raise LotFullError(size)
        self._spots[spot] = plate
        self._where[plate] = spot
        return spot

    def leave(self, plate):
        plate = _clean(plate)
        if plate not in self._where:
            raise NotParkedError(plate)
        spot = self._where.pop(plate)
        self._spots[spot] = None
        return spot

    def where(self, plate):
        return self._where.get(_clean(plate))

    def free(self, kind):
        if kind not in SIZES:
            raise ValueError(f"kind must be 'small' or 'large', got {kind!r}")
        prefix = "S" if kind == "small" else "L"
        return sum(1 for name, plate in self._spots.items() if name.startswith(prefix) and plate is None)

    def report(self):
        return [f"{name} {plate}" for name, plate in self._spots.items() if plate is not None]
