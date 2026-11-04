n = int(input())
a = [int(x) for x in input().split()]

values = set(a)
best = 0
for x in values:
    if x - 1 not in values:
        length = 1
        while x + length in values:
            length += 1
        best = max(best, length)
print(best)
