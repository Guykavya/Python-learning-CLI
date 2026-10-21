n = int(input())
balanced = 0
for _ in range(n):
    line = input()
    depth = 0
    deepest = 0
    for pos, ch in enumerate(line):
        if ch == "(":
            depth += 1
            deepest = max(deepest, depth)
        elif ch == ")":
            depth -= 1
            if depth < 0:
                print(f"Unbalanced: unexpected ')' at position {pos}")
                break
    else:
        if depth > 0:
            print(f"Unbalanced: {depth} unclosed '('")
        else:
            print(f"Balanced, max depth {deepest}")
            balanced += 1
print(f"Balanced: {balanced} of {n}")
