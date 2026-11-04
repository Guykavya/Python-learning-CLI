n = int(input())
a = [int(x) for x in input().split()]
exp = 1
biggest = max(a)
while biggest // exp > 0:
    buckets = [[] for _ in range(10)]
    for x in a:
        buckets[(x // exp) % 10].append(x)
    a = [x for bucket in buckets for x in bucket]
    exp *= 10
print(" ".join(map(str, a)))
