n = int(input())
a = [int(x) for x in input().split()]
# TODO: count inversions in O(n log n) with a merge sort
count = 0
for i in range(n):
    for j in range(i + 1, n):
        if a[i] > a[j]:
            count += 1
print(count)
