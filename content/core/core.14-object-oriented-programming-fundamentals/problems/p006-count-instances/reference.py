class Ticket:
    count = 0

    def __init__(self, title):
        self.title = title
        Ticket.count += 1
        self.number = Ticket.count

    @classmethod
    def reset(cls):
        cls.count = 0

    @classmethod
    def how_many(cls):
        return cls.count
