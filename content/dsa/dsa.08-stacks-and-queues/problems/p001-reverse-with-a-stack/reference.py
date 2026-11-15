def reverse_string(s):
    stack = []
    for ch in s:
        stack.append(ch)
    out = []
    while stack:
        out.append(stack.pop())
    return "".join(out)
