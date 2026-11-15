n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
for _ in range(q):
    l, r, v = map(int, input().split())
    # TODO: mark +v at l and -v at r + 1 in a difference array (do not loop over the range)
# TODO: running total over the marks, add it to each element
print(*a)
