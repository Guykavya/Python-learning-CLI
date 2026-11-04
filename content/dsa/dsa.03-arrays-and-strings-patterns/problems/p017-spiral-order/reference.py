r, c = map(int, input().split())
g = [input().split() for _ in range(r)]

top, bottom, left, right = 0, r - 1, 0, c - 1
out = []
while top <= bottom and left <= right:
    for col in range(left, right + 1):
        out.append(g[top][col])
    top += 1
    for row in range(top, bottom + 1):
        out.append(g[row][right])
    right -= 1
    if top <= bottom:
        for col in range(right, left - 1, -1):
            out.append(g[bottom][col])
        bottom -= 1
    if left <= right:
        for row in range(bottom, top - 1, -1):
            out.append(g[row][left])
        left += 1

print(" ".join(out))
