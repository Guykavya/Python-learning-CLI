def daily_temperatures(temps):
    wait = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            wait[j] = i - j
        stack.append(i)
    return wait
