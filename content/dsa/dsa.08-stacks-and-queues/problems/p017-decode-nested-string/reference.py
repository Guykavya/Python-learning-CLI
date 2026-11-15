def decode(s):
    stack = []
    current = ""
    k = 0
    for ch in s:
        if ch.isdigit():
            k = k * 10 + int(ch)
        elif ch == "[":
            stack.append((current, k))
            current, k = "", 0
        elif ch == "]":
            outer, times = stack.pop()
            current = outer + current * times
        else:
            current += ch
    return current
