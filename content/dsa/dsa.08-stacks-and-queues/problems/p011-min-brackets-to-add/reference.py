def brackets_to_add(s):
    opens = 0
    open_count = 0
    for ch in s:
        if ch == "(":
            open_count += 1
        elif open_count:
            open_count -= 1
        else:
            opens += 1
    return (opens, open_count)
