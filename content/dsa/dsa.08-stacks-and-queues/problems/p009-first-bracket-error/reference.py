PAIRS = {")": "(", "]": "[", "}": "{"}


def bracket_error(text):
    stack = []
    for i, ch in enumerate(text):
        if ch in "([{":
            stack.append((ch, i))
        elif ch in PAIRS:
            if not stack:
                return (i, "unexpected")
            if stack[-1][0] != PAIRS[ch]:
                return (i, "mismatch")
            stack.pop()
    if stack:
        return (stack[0][1], "unclosed")
    return (-1, "ok")
