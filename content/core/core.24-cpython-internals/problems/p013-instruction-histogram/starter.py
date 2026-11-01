import dis
from collections import Counter


def opcode_histogram(obj, recursive=False):
    """Counter of opnames in obj's bytecode (plus nested code objects if recursive)."""
    # TODO: count i.opname for i in dis.get_instructions(...)
    # TODO: if recursive, also walk the code objects in co_consts (at any depth)
    return Counter()


def by_prefix(hist):
    """Group a histogram by the part of each opname before the first underscore."""
    # TODO
    return Counter()
