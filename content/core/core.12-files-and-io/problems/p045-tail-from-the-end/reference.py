def tail_lines(path, n=10, block_size=4096):
    if n <= 0:
        return []
    with open(path, "rb") as f:
        f.seek(0, 2)
        pos = f.tell()
        data = b""
        while pos > 0 and data.count(b"\n") <= n:
            step = min(block_size, pos)
            pos -= step
            f.seek(pos)
            data = f.read(step) + data
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    result = []
    for line in lines[-n:]:
        if line.endswith(b"\r"):
            line = line[:-1]
        result.append(line.decode("utf-8"))
    return result
