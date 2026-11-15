## Approach

A list of chains, each chain a list of `[key, value]` pairs. A helper scans one chain. `put` updates in place or appends and, on a new key, checks the
load factor. Rehashing collects all pairs (bucket 0 first) into one list and inserts them into a new table with the doubled size.

## Code

```python
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
```

## Complexity

`put`, `get` and `del` cost the length of one chain: O(1) on average while the load factor stays below 0.75. A resize costs O(m + size) but happens
only when the size doubles, so the cost is O(1) amortised per insert. `maxchain` scans all buckets: O(m) per call.

## Another way

Open addressing (linear probing) keeps keys in one flat array with no inner lists; it is more cache friendly but needs tombstones for deletion.
Python's own `dict` uses open addressing with a smarter probe sequence and a separate compact array for entries.
