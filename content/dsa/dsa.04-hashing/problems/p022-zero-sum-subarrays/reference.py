n = int(input())
a = [int(x) for x in input().split()]

seen = {0: 1}
s = 0
answer = 0
for x in a:
    s += x
    answer += seen.get(s, 0)
    seen[s] = seen.get(s, 0) + 1
print(answer)
