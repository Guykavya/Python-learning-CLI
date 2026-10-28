class ParkingError(Exception):
    pass


class LotFullError(ParkingError):
    pass


class AlreadyParkedError(ParkingError):
    pass


class NotParkedError(ParkingError):
    pass


class ParkingLot:
    def __init__(self, small, large):
        # TODO: create the spots S1.. and L1..
        pass

    def park(self, plate, size):
        return None

    def leave(self, plate):
        return None

    def where(self, plate):
        return None

    def free(self, kind):
        return 0

    def report(self):
        return []
