rows = [[1]]
for n in range(1, 61):
    prev = rows[n - 1]
    row = [1]
    for r in range(1, n):
        row.append(prev[r - 1] + prev[r])
    row.append(1)
    rows.append(row)

q = int(input())
for _ in range(q):
    n, r = (int(x) for x in input().split())
    print(rows[n][r] if r <= n else 0)
