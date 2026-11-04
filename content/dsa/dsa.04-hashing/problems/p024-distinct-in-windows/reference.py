n, k = map(int, input().split())
a = [int(x) for x in input().split()]

count = {}
for x in a[:k]:
    count[x] = count.get(x, 0) + 1
answer = [len(count)]

for i in range(k, n):
    x = a[i]
    count[x] = count.get(x, 0) + 1
    old = a[i - k]
    count[old] -= 1
    if count[old] == 0:
        del count[old]
    answer.append(len(count))

print(*answer)
