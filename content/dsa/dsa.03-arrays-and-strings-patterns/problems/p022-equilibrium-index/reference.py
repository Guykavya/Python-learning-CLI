n = int(input())
a = [int(x) for x in input().split()]

total = sum(a)
left = 0
answer = -1
for i in range(n):
    right = total - left - a[i]      # everything after position i
    if left == right:
        answer = i + 1               # 1-based
        break
    left += a[i]

print(answer)
