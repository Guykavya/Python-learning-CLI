n, target = map(int, input().split())
a = [int(x) for x in input().split()]

seen = {}
for j, x in enumerate(a):
    need = target - x
    if need in seen:
        print(seen[need], j)
        break
    seen[x] = j
