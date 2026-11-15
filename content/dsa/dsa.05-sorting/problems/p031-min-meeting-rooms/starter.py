n = int(input())
meetings = []
for _ in range(n):
    s, e = map(int, input().split())
    meetings.append((s, e))
# TODO: minimum number of rooms = largest number of meetings running at once
print(n)
