n = int(input())
meetings = []
for _ in range(n):
    s, e = map(int, input().split())
    meetings.append((s, e))
meetings.sort()
ok = True
for i in range(1, n):
    if meetings[i][0] < meetings[i - 1][1]:
        ok = False
        break
print("YES" if ok else "NO")
