n = int(input())
a = [int(x) for x in input().split()]
target = int(input())

i, j = 0, n - 1
answer = "-1"
while i < j:
    s = a[i] + a[j]
    if s == target:
        answer = f"{i + 1} {j + 1}"
        break
    if s < target:
        i += 1
    else:
        j -= 1

print(answer)
