n, k = map(int, input().split())
a = [int(x) for x in input().split()]

seen = {}
answer = 0
for x in a:
    answer += seen.get(k - x, 0)
    seen[x] = seen.get(x, 0) + 1
print(answer)
