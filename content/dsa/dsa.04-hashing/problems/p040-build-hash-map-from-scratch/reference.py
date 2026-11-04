m = 8
table = [[] for _ in range(m)]
size = 0


def find(key):
    chain = table[key % m]
    for pos in range(len(chain)):
        if chain[pos][0] == key:
            return pos
    return -1


def rehash():
    global m, table
    pairs = []
    for chain in table:
        for pair in chain:
            pairs.append(pair)
    m *= 2
    table = [[] for _ in range(m)]
    for pair in pairs:
        table[pair[0] % m].append(pair)


q = int(input())
for _ in range(q):
    parts = input().split()
    cmd = parts[0]
    if cmd == "put":
        k, v = int(parts[1]), int(parts[2])
        pos = find(k)
        if pos >= 0:
            table[k % m][pos][1] = v
        else:
            table[k % m].append([k, v])
            size += 1
            if size * 4 > m * 3:
                rehash()
    elif cmd == "get":
        k = int(parts[1])
        pos = find(k)
        print(table[k % m][pos][1] if pos >= 0 else "none")
    elif cmd == "del":
        k = int(parts[1])
        pos = find(k)
        if pos >= 0:
            table[k % m].pop(pos)
            size -= 1
            print("ok")
        else:
            print("missing")
    elif cmd == "size":
        print(size)
    elif cmd == "buckets":
        print(m)
    else:
        print(max(len(chain) for chain in table))
