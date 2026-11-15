n = int(input())
ans = 0
for x in input().split():
    ans ^= int(x)
print(ans)
