index = {}
n = int(input())
for number in range(1, n + 1):
    for word in input().lower().split():
        index.setdefault(word, set()).add(number)
for _ in range(int(input())):
    op, *words = input().lower().split()
    sets = [index.get(w, set()) for w in words]
    if op == "and":
        result = set(sets[0])
        for s in sets[1:]:
            result &= s
    elif op == "or":
        result = set()
        for s in sets:
            result |= s
    else:
        result = sets[0] - sets[1]
    print(" ".join(str(d) for d in sorted(result)) if result else "none")
