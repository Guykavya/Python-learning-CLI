n = int(input())
meetings = []
for _ in range(n):
    s, e = map(int, input().split())
    meetings.append((s, e))
# TODO: YES if no two meetings overlap (touching is fine), else NO
print("YES")
