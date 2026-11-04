s = input().strip()
L = int(input())

seen = set()
repeated = set()
for i in range(len(s) - L + 1):
    seg = s[i:i + L]
    if seg in seen:
        repeated.add(seg)
    else:
        seen.add(seg)

result = sorted(repeated)
print(len(result))
print(*result)
