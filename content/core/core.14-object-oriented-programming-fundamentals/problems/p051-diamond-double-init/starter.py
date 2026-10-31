# This code works for Printer and Scanner, but a Copier is broken.
# Run it and look at Device.connections and copier.log. Then make it cooperative.


class Device:
    connections = 0  # how many times a connection was opened

    def __init__(self, name):
        self.name = name
        self.log = []
        Device.connections += 1
        self.log.append("Device")


class Printer(Device):
    def __init__(self, name, dpi=300):
        Device.__init__(self, name)
        self.dpi = dpi
        self.log.append("Printer")


class Scanner(Device):
    def __init__(self, name, colour=True):
        Device.__init__(self, name)
        self.colour = colour
        self.log.append("Scanner")


class Copier(Printer, Scanner):
    def __init__(self, name, dpi=300, colour=True, copies_per_minute=20):
        Printer.__init__(self, name, dpi)
        Scanner.__init__(self, name, colour)
        self.copies_per_minute = copies_per_minute
        self.log.append("Copier")
