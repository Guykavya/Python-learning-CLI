n = int(input())
a = [int(x) for x in input().split()]
q = int(input())

for _ in range(q):
    l, r = map(int, input().split())
    i, j = l - 1, r - 1
    while i < j:
        a[i], a[j] = a[j], a[i]
        i += 1
        j -= 1

print(*a)
