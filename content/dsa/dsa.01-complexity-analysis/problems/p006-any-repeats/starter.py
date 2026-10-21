n = int(input())
a = [int(x) for x in input().split()]

# Correct but slow: about n * n / 2 comparisons.
found = False
for i in range(n):
    for j in range(i + 1, n):
        if a[i] == a[j]:
            found = True
if found:
    print("YES")
else:
    print("NO")
