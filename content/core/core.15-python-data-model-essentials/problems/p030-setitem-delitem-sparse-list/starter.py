class SparseList:
    def __init__(self, size, default=0):
        # TODO: store only the positions that differ from the default (a dict)
        self.default = default
        self._size = size

    def __len__(self):
        return self._size
