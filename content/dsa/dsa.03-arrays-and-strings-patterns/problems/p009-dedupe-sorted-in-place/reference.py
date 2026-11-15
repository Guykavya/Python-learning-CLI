n = int(input())
a = [int(x) for x in input().split()]

w = 0
for r in range(n):
    if w == 0 or a[r] != a[w - 1]:
        a[w] = a[r]
        w += 1

print(w)
print(*a[:w])
