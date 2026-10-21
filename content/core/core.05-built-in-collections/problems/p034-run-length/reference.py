runs = []
for token in input().split():
    if runs and runs[-1][0] == token:
        runs[-1][1] += 1
    else:
        runs.append([token, 1])
pieces = [t if n == 1 else f"{t}*{n}" for t, n in runs]
print(" ".join(pieces) if pieces else "(empty)")
print("Runs:", len(runs))
