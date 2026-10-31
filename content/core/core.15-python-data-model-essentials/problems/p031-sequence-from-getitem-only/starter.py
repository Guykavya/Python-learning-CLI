class Multiples:
    def __init__(self, step, count):
        self.step = step
        self.count = count

    def __getitem__(self, index):
        raise IndexError(index)      # TODO: return step * (index + 1) for 0 <= index < count


class Backwards:
    def __init__(self, seq):
        self.seq = seq
