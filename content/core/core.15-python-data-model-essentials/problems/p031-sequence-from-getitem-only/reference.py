class Multiples:
    """Only __getitem__: no __iter__, no __len__."""

    def __init__(self, step, count):
        self.step = step
        self.count = count

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("indices must be integers")
        if not 0 <= index < self.count:
            raise IndexError(index)
        return self.step * (index + 1)


class Backwards:
    """Reads another sequence from the end. Needs __len__ and __getitem__ (reversed() uses them)."""

    def __init__(self, seq):
        self.seq = seq

    def __len__(self):
        return len(self.seq)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("indices must be integers")
        if not 0 <= index < len(self.seq):
            raise IndexError(index)
        return self.seq[len(self.seq) - 1 - index]
