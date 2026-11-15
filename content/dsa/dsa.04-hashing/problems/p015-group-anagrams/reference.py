n = int(input())
words = input().split()

groups = {}
for w in words:
    key = "".join(sorted(w))
    if key not in groups:
        groups[key] = []
    groups[key].append(w)

result = [sorted(g) for g in groups.values()]
result.sort(key=lambda g: g[0])
for g in result:
    print(*g)
