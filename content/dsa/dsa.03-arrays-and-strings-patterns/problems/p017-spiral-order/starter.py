r, c = map(int, input().split())
g = [input().split() for _ in range(r)]
# TODO: keep top, bottom, left, right; walk the four sides and shrink them
out = []
for row in g:
    out.extend(row)
print(" ".join(out))
