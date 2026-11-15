n = int(input())
a = [int(x) for x in input().split()]

p = [0]
for x in a:
    p.append(p[-1] + x)

print(*p)
