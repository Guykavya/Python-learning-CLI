class Device:
    connections = 0  # how many times a connection was opened

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.log = ["Device"]
        Device.connections += 1


class Printer(Device):
    def __init__(self, *, dpi=300, **kwargs):
        super().__init__(**kwargs)
        self.dpi = dpi
        self.log.append("Printer")


class Scanner(Device):
    def __init__(self, *, colour=True, **kwargs):
        super().__init__(**kwargs)
        self.colour = colour
        self.log.append("Scanner")


class Copier(Printer, Scanner):
    def __init__(self, name, *, dpi=300, colour=True, copies_per_minute=20):
        super().__init__(name=name, dpi=dpi, colour=colour)
        self.copies_per_minute = copies_per_minute
        self.log.append("Copier")
