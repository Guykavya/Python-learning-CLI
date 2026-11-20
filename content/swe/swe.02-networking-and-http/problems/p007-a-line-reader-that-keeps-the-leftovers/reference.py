MAX_LINE = 64 * 1024


class LineReader:
    def __init__(self):
        self.buffer = b""

    def feed(self, chunk):
        self.buffer += chunk
        lines = []
        while True:
            i = self.buffer.find(b"\n")
            if i == -1:
                break
            raw, self.buffer = self.buffer[:i], self.buffer[i + 1:]
            if raw.endswith(b"\r"):
                raw = raw[:-1]
            lines.append(raw.decode("utf-8"))
        if len(self.buffer) > MAX_LINE:
            raise ValueError("line too long")
        return lines
