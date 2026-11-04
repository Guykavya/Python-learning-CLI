n = int(input())
a = [int(x) for x in input().split()]
swaps = 0
for i in range(n - 1):
    m = i
    for j in range(i + 1, n):
        if a[j] < a[m]:
            m = j
    if m != i:
        a[i], a[m] = a[m], a[i]
        swaps += 1
print(" ".join(map(str, a)))
print(swaps)
