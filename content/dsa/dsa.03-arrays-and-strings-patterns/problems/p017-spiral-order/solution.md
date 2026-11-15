## Approach

The four boundaries describe the ring that is not yet visited. Each side walk takes one edge of that ring and then
shrinks the ring on that side. The two extra checks stop the last, thin ring (a single row or a single column) from
being walked twice, once forwards and once backwards.

## Code

```python
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
```

## Complexity

O(r * c) time: each cell is taken once. O(r * c) memory for the output list (the grid itself is already that big).

## Another way

Simulate a walker: keep a direction (right, down, left, up) and a `seen` grid. Step forward; if the next cell is
outside the grid or already seen, turn right instead. It is easier to get right at the edges, but it needs the extra
`seen` grid. The boundary version uses O(1) extra memory besides the output.
