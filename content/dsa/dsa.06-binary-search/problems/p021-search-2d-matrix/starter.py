r, c = map(int, input().split())
m = [[int(x) for x in input().split()] for _ in range(r)]
q = int(input())
queries = [int(x) for x in input().split()]
# TODO: for every query print "row col" (0-based) or "-1 -1"
for x in queries:
    print(-1, -1)
