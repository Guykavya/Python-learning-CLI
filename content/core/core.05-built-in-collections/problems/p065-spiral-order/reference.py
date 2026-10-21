r, c = [int(x) for x in input().split()]
m = [[int(x) for x in input().split()] for _ in range(r)]
out = []
top, bottom, left, right = 0, r - 1, 0, c - 1
while top <= bottom and left <= right:
    for j in range(left, right + 1):
        out.append(m[top][j])
    top += 1
    for i in range(top, bottom + 1):
        out.append(m[i][right])
    right -= 1
    if top <= bottom:
        for j in range(right, left - 1, -1):
            out.append(m[bottom][j])
        bottom -= 1
    if left <= right:
        for i in range(bottom, top - 1, -1):
            out.append(m[i][left])
        left += 1
print(" ".join(str(v) for v in out))
