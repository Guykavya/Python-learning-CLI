import sys

data = sys.stdin.read().split()
n = int(data[0])
adj = [[] for _ in range(n + 1)]
for i in range(n - 1):
    u = int(data[1 + 2 * i])
    v = int(data[2 + 2 * i])
    adj[u].append(v)
    adj[v].append(u)

depth = [-1] * (n + 1)
depth[1] = 0
stack = [1]
while stack:
    u = stack.pop()
    for v in adj[u]:
        if depth[v] == -1:
            depth[v] = depth[u] + 1
            stack.append(v)
print(max(depth[1:]), sum(depth[1:]))
