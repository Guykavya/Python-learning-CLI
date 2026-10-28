from contextlib import ExitStack


def read_all(paths):
    """Open all files at once, read each, and return the list of contents."""
    with ExitStack() as stack:
        files = [stack.enter_context(open(path)) for path in paths]
        return [f.read() for f in files]


def merge_lines(paths):
    """Open all files at once and return the lines side by side, stopping at the shortest file."""
    with ExitStack() as stack:
        files = [stack.enter_context(open(path)) for path in paths]
        return [tuple(line.rstrip("\n") for line in lines) for lines in zip(*files)]
