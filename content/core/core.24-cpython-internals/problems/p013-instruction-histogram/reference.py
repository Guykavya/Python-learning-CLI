import dis
import types
from collections import Counter


def opcode_histogram(obj, recursive=False):
    """Counter of opnames in obj's bytecode (plus nested code objects if recursive)."""
    code = obj if isinstance(obj, types.CodeType) else obj.__code__
    hist = Counter(ins.opname for ins in dis.get_instructions(code))
    if recursive:
        for const in code.co_consts:
            if isinstance(const, types.CodeType):
                hist += opcode_histogram(const, recursive=True)
    return hist


def by_prefix(hist):
    """Group a histogram by the part of each opname before the first underscore."""
    grouped = Counter()
    for name, count in hist.items():
        grouped[name.split("_", 1)[0]] += count
    return grouped
