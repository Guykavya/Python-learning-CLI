s = input().strip()
t = input().strip()

forward = {}
backward = {}
answer = "YES"
for a, b in zip(s, t):
    if forward.get(a, b) != b or backward.get(b, a) != a:
        answer = "NO"
        break
    forward[a] = b
    backward[b] = a
print(answer)
