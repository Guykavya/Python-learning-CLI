n = int(input())
a = [int(x) for x in input().split()]

g = 0
for x in a:
    u, v = g, x
    while v:
        u, v = v, u % v
    g = u

print(g)
print(sum(1 for x in a if x == g))
print(sum(x // g for x in a))
