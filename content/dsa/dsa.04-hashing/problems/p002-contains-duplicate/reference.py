n = int(input())
a = [int(x) for x in input().split()]

seen = set()
answer = "NO"
for x in a:
    if x in seen:
        answer = "YES"
        break
    seen.add(x)
print(answer)
