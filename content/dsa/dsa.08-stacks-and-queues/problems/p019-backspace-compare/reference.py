def type_text(s):
    buffer = []
    for ch in s:
        if ch == "#":
            if buffer:
                buffer.pop()
        else:
            buffer.append(ch)
    return "".join(buffer)


def next_kept(s, i):
    skip = 0
    while i >= 0:
        if s[i] == "#":
            skip += 1
        elif skip:
            skip -= 1
        else:
            return i
        i -= 1
    return -1


def backspace_equal(a, b):
    i, j = len(a) - 1, len(b) - 1
    while True:
        i = next_kept(a, i)
        j = next_kept(b, j)
        if i < 0 or j < 0:
            return i < 0 and j < 0
        if a[i] != b[j]:
            return False
        i -= 1
        j -= 1
