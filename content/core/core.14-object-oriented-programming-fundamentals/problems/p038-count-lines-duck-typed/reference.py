def count_nonblank(source, comment=None):
    if isinstance(source, str):
        raise TypeError("pass lines, not one string (try text.splitlines())")
    count = 0
    for line in source:
        text = line.strip()
        if not text:
            continue
        if comment is not None and text.startswith(comment):
            continue
        count += 1
    return count


def first_line(source):
    for line in source:
        text = line.strip()
        if text:
            return text
    return None


class Lines:
    def __init__(self, text):
        self.text = text

    def __iter__(self):
        for line in self.text.splitlines():
            yield line
