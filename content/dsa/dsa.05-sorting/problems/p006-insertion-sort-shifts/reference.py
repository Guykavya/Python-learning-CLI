n = int(input())
a = [int(x) for x in input().split()]
shifts = 0
for i in range(1, n):
    key = a[i]
    j = i - 1
    while j >= 0 and a[j] > key:
        a[j + 1] = a[j]
        shifts += 1
        j -= 1
    a[j + 1] = key
print(" ".join(map(str, a)))
print(shifts)
