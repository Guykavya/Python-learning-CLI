n, m = map(int, input().split())
a = [int(x) for x in input().split()]
b = [int(x) for x in input().split()]
out = []
i = j = 0
while i < n and j < m:
    if a[i] <= b[j]:
        out.append(a[i])
        i += 1
    else:
        out.append(b[j])
        j += 1
out.extend(a[i:])
out.extend(b[j:])
print(" ".join(map(str, out)))
