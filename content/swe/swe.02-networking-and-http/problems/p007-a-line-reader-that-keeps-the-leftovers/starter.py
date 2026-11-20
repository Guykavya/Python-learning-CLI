MAX_LINE = 64 * 1024


class LineReader:
    def __init__(self):
        self.buffer = b""

    def feed(self, chunk):
        # TODO: append, cut complete lines, keep the leftover, enforce MAX_LINE
        return []
