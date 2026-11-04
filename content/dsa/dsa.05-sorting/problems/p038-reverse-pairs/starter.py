n = int(input())
a = [int(x) for x in input().split()]
# TODO: count pairs i < j with a[i] > 2 * a[j] in O(n log n)
count = 0
for i in range(n):
    for j in range(i + 1, n):
        if a[i] > 2 * a[j]:
            count += 1
print(count)
