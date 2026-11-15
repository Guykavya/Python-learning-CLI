c = int(input())
q = int(input())
cache = {}
out = []
for _ in range(q):
    parts = input().split()
    if parts[0] == "get":
        k = int(parts[1])
        if k in cache:
            v = cache.pop(k)
            cache[k] = v
            out.append(v)
        else:
            out.append(-1)
    else:
        k = int(parts[1])
        v = int(parts[2])
        if k in cache:
            del cache[k]
        elif len(cache) == c:
            del cache[next(iter(cache))]
        cache[k] = v
print("\n".join(map(str, out)))
