n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

seen = {0: 1}          # prefix sum 0 occurs once: the empty prefix before index 0
prefix = 0
count = 0
for x in a:
    prefix += x
    count += seen.get(prefix - k, 0)     # earlier prefixes p with prefix - p == k
    seen[prefix] = seen.get(prefix, 0) + 1

print(count)
