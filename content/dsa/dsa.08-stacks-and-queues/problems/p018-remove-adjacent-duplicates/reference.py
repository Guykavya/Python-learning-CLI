def remove_duplicates(s):
    stack = []
    pairs = 0
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
            pairs += 1
        else:
            stack.append(ch)
    return ("".join(stack), pairs)
