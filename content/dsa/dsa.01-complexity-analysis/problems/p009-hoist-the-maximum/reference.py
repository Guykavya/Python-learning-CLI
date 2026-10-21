n = int(input())
a = [int(x) for x in input().split()]

best = max(a)            # computed once: O(n)
top = 0
half = 0
for x in a:
    if x == best:
        top += 1
    if 2 * x >= best:
        half += 1
print(top)
print(half)
