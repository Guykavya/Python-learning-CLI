groups = {}
for w in input().split():
    groups.setdefault(len(w), set()).add(w)
for length in sorted(groups):
    print(f"{length}: {' '.join(sorted(groups[length]))}")
