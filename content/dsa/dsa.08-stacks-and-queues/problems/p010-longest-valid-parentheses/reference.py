def longest_valid(s):
    stack = [-1]
    best_start, best_len = 0, 0
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                length = i - stack[-1]
                if length > best_len:
                    best_start, best_len = stack[-1] + 1, length
    return s[best_start:best_start + best_len]
