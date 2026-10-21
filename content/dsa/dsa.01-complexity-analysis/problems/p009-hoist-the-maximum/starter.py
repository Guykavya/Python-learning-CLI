n = int(input())
a = [int(x) for x in input().split()]

# Correct but slow: max(a) is itself a loop over all n scores, and it runs 2n times.
top = 0
half = 0
for i in range(n):
    if a[i] == max(a):
        top += 1
    if 2 * a[i] >= max(a):
        half += 1
print(top)
print(half)
