n = int(input())
a = [int(x) for x in input().split()]
passes = swaps = 0
while True:
    passes += 1
    swapped = False
    for i in range(n - 1):
        if a[i] > a[i + 1]:
            a[i], a[i + 1] = a[i + 1], a[i]
            swaps += 1
            swapped = True
    if not swapped:
        break
print(passes)
print(swaps)
print(" ".join(map(str, a)))
