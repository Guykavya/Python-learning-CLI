friends = {}
for _ in range(int(input())):
    a, b = input().split()
    friends.setdefault(a, set()).add(b)
    friends.setdefault(b, set()).add(a)
for _ in range(int(input())):
    person = input().strip()
    mine = friends.get(person, set())
    counts = {}
    for f in mine:
        for g in friends[f]:
            if g != person and g not in mine:
                counts[g] = counts.get(g, 0) + 1
    top = sorted((-c, g) for g, c in counts.items())[:3]
    if top:
        print(f"{person}: " + ", ".join(f"{g} ({-c})" for c, g in top))
    else:
        print(f"{person}: no suggestions")
