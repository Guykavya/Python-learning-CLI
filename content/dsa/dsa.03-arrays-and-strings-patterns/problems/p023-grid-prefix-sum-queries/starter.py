r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]
# TODO: build P with an extra zero row and column, then answer each query with four lookups
q = int(input())
for _ in range(q):
    r1, c1, r2, c2 = [int(x) for x in input().split()]
    print(0)
