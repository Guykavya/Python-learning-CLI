r, c = map(int, input().split())
g = [input().split() for _ in range(r)]
# TODO: output row j is input column j (print c lines of r values)
for row in g:
    print(*row)
