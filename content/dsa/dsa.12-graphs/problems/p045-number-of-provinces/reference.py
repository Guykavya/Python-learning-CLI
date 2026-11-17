def count_provinces(is_connected):
    n = len(is_connected)
    seen = [False] * n
    provinces = 0
    for s in range(n):
        if seen[s]:
            continue
        provinces += 1                             # a new province starts here
        seen[s] = True
        stack = [s]
        while stack:
            u = stack.pop()
            for v in range(n):
                if is_connected[u][v] == 1 and not seen[v]:
                    seen[v] = True
                    stack.append(v)
    return provinces
