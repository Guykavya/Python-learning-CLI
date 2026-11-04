c = int(input())
q = int(input())
# TODO: a dict keeps insertion order: pop and reinsert on every use; evict next(iter(cache)) when full
for _ in range(q):
    parts = input().split()
    if parts[0] == "get":
        print(-1)
