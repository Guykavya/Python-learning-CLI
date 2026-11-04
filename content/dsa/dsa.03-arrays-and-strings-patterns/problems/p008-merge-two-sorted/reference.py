n = int(input())
a = [int(x) for x in input().split()]
m = int(input())
b = [int(x) for x in input().split()]

i = j = 0
out = []
while i < n and j < m:
    if a[i] <= b[j]:
        out.append(a[i])
        i += 1
    else:
        out.append(b[j])
        j += 1
out.extend(a[i:])
out.extend(b[j:])

print(*out)
